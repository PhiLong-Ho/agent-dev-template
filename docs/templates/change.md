# Change: <name>

## Contract before implementation

Requirements/criteria, owning spec, affected surfaces/states, exclusions and risks.
Test plan: focused iteration checks, completed-candidate gates and exclusions.

## Architecture preflight

- Impact: affected owners/contracts/invariants, or N/A with source-based reason.
- Fresh expert identity, source/diagram scope and explicit approach verdict.
- Current/proposed overview and sequence; alternatives and failure/cancel/stale/rollback paths.
- Settled approach, material questions/user decision, compatibility/migration and tests.
- Changed diagrams/render inspection; material departure re-review.

## UI preflight

Expert identity/scope/current captures; recommended before/after task and sketch;
states/tradeoffs; material questions; actual user answer or exact authorization;
independent work while waiting; settled spec/design/acceptance and departures.
Use N/A with reason for non-UI work.

## Implementation and verification

Ownership/shared state/style, changed diagrams and rendered review; actual commands,
source/tree, configuration, raw outcomes, acceptance/E2E scope and gaps. Distinguish
rendered/golden approval from measurements. Record timing boundaries/samples and
p50/p95 for performance. Never infer scenario passes from mapping/assertion totals.
Record available command/suite/review/evidence durations and rerun reasons, reused
evidence with source/test/configuration bindings and original execution, and reusable
workflow alignment with adopting projects or explicit pending companion scope.

## Evidence and delivery

Compact summary/descriptor, verified ZIP/member hashes and reviewer access;
actual local/pending/uploaded location/retention; coverage refresh/report/snapshot;
two actual fresh final reviewers and candidate digest; gate/PR/CI/release links.

## Release architecture (required for every new version, not task N/A)

- Exact pre-attestation tree/digest and version/previous release baseline:
- Fresh expert identity/UTC, actual scope/findings/verdict/blockers/gaps:
- Attestation-only delta verified by two different fresh final reviewers:
- Final canonical digest includes the record; no extra exclusions:
- Any changed input/re-review or byte-identical same-version transport retry reason:
- Release authorization blocked until actual approval and blockers resolved:
