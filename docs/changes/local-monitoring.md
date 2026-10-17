# Change: local command monitoring

## Contract before implementation

User authorized a free local streaming runner and separate status view. Baseline
NFR-009 / WF-MONITOR-001 and the owning local-monitoring feature contract precede
implementation. DexDroid's companion is NFR-011 / DX-OBSERVE-001. Preserve existing
required checks, independent reviews and release validation. No cloud, model-call,
agent-session collector, auto-retry or Android product UI change is included.

## Experience preflight

Read-only advisor `/root/monitor_experience_preflight` inspected both existing
flows. Before: buffered command with limited visibility. After: run normally and
attach another read-only terminal to its printed directory. Distinguish heartbeat,
activity, progress, quiet/stale warning and actual outcome; viewer Ctrl+C detaches.
Runner cancellation and restoration remain explicit. The user had approved these
local defaults with "proceed"; no material unresolved choice or app UI capture applies.

## Implementation and acceptance

The same standard-library supervisor and host acceptance cases live in both repos.
Windows Job Objects/POSIX process groups own ordinary descendants; direct raw
writers, bounded events, atomic status and an independent viewer need no network.
Template quality/build adapters retain legacy combined logs, enforce configurable
deadlines, preserve failure across later success, and bind quality source context.
DexDroid adapts instrumentation and records preflight/restoration. Interrupted
execution cannot become success and timeout retains stdout plus stderr.

Tests exercise observable output before exit, separate raw bytes, independent
observation, quiet warnings, timeouts/cancellation, descendant cleanup, nonzero/
launch failure, output/event limits, capture/extractor errors, bounded malformed/
stale status, chunked progress and viewer detach. Existing adapter/release tests
remain applicable; there are no production Android input/style changes.

Architecture and feature flow diagrams are reconciled with these owners; rendered
inspection is separate from product visual approval. Current host runs and compact
evidence index use `testresults/0.1.0/local-monitoring/`; raw bytes stay ignored and
available locally to reviewers. Test-source changes refresh generated coverage.
Prior coding-practice guidance is included in this candidate as requested.

## Limits and pending verification

Legacy Android tests may buffer progress until their final result. No per-scenario
producer or selector is added. Host device fixtures mock ADB; real monitor/OEM
timeout/interrupt/restoration and current installed device builds remain unverified.
Windows execution and POSIX execution have distinct scopes; no speedup claim follows
from assertion counts. Raw logs can contain sensitive output and stay local. Viewer
snapshots are informational; owning result/source validators decide acceptance.
No publication/release or automatic retention/deletion is performed by the monitor.

Final corrections cover suspended Windows launch before job assignment, deadline
enforcement independent from slow extraction, accurate interrupted-restoration
state, and tracked compact evidence descriptors. Regression cases exercise these
observable failures; earlier candidate evidence remains historical.

Finalization regressions also cover asynchronous post-command monitor faults and
the final-event cap. Authoritative runner/host/build outcomes refuse success while
preserving child exit and independent controller-restoration evidence.

Observer CLI regressions distinguish missing/invalid/stale state (exit 2) from
observed non-success. Template adapters retain previously valid command names
through bounded internal labels without changing exact outcome/log names.
