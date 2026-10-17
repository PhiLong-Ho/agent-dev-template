# Latest approved UI references

This is the **master reference set**, not a test-run archive. Keep one latest approved
PNG per required screen/state/configuration and its catalog entry. A contact sheet
may aid browsing but never replaces full-resolution views. This CLI starter explicitly
declares no-ui; no screenshot or visual approval is invented.

For a UI project set catalog.json mode to ui, declare source_patterns for relevant
UI/state/design sources and stable required_states such as phone/main/portrait,
phone/settings/expanded and monitor/layout/r90. Include applicable keyboard,
loading/error, bounds, rotation and accessibility states. The owning spec defines
the actual matrix; catalog coverage is not E2E execution.

For every UI change:

1. Compare expert proposals/current captures with these references first.
2. Capture and inspect affected views using the current build and declared
   configuration; run behavioral acceptance separately.
3. Obtain actual visual approval under the project/user decision policy.
   A copied timestamp or CI hash is never visual judgment.
4. Replace affected master PNGs and retain historical raw captures in evidence
   archives. Reconcile required states and source fingerprints. Changed source
   with identical renders still needs inspected evidence explaining retained views.
5. Record state, image (relative here), sha256, dimensions ([width,height]),
   configuration, evidence (durable raw archive/link), reviewer (actual identity)
   and UTC approved_at for every entry. Catalog source_hashes contains the complete
   relevant source map, not a guessed screenshot commit.

~~~sh
python tools/ui_reference.py fingerprint
python tools/ui_reference.py check
~~~

Fingerprint prints hashes for **reviewed reconciliation**, never writes approval.
Check runs in quality CI and rejects missing/duplicate states, corrupt/changed
images, missing approval metadata and stale relevant source hashes. Approval is
attested, not authenticated. The gate does not judge pixels or discover undeclared
UI sources. Intentional small master images are versioned; historical/test captures
stay in ignored runs, Actions artifacts and release archives. All are excluded
from graph inputs.
