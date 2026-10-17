# Local monitoring verification

Windows 11 / Python 3.13.5. Candidate based on cb4263e; host-final-cli source fingerprints
and unchanged-source outcome bind the actual dirty candidate code/docs/tests.

- Full corrected host: 95 passed, no failures/errors, one existing POSIX-only skip.
  Formatting, lint, requirements, coverage, documentation and UI-reference gates pass.
- Real subprocess fixtures exercise bytes available before exit, independent observer,
  quiet warnings, deadlines/cancel, owned descendant cleanup, capture/extractor/limit
  failures, stale/malformed bounded state and pending-result reset across commands.
- Configured command deadline failure remains failed after a later successful command.
  Tooling case-start events were visible in an independent terminal during the run;
  the active command stayed pending and source fingerprints matched after completion.
- Actual terminal output and both diagram renders were inspected. Diagram sources
  match the template. No product UI exists; no screenshot baseline is approved.

Commands: tools/quality.py --evidence .../host-final-cli, coverage update/check,
check_docs.py, check_requirements.py, Ruff, shared native Mermaid render/inspection,
and tools/run_monitor.py status while host-final was running. Earlier host/host-final
evidence precedes suspended Windows launch, independent extraction/deadline handling
and restoration-interrupt corrections; these earlier attempts are historical. Fixture
publication messages use mocked remotes, never actual GitHub publication.

[Archive descriptor](archive.json) identifies the verified local-only ZIP
at .local/monitor-evidence/host-final-cli/evidence.zip. Raw originals remain ignored under
testresults/0.1.0/runs/20261017-local-monitoring/. Verify bytes/member hashes with
tools/evidence.py verify. Nothing is uploaded by local packaging.

Remaining gaps: POSIX cleanup/private-mode execution, hosted Windows/Ubuntu CI,
model/provider telemetry, measured resource overhead and hosted release publication.
Android adapter evidence belongs to DexDroid's separately scoped record (one normal
icon suite/restoration, not real timeout/cancel or broad device certification).

Current regressions also cover final-event limits and asynchronous post-command
monitoring faults: final runner/host acceptance refuses success. Normal device
restoration remains independent. No new broad device or release claim is made.

Latest final-cli runs include actual subprocess observer exit-code checks and
valid configured-name compatibility regressions. Earlier accepted/sealed runs
precede these corrections and remain historical.
