# Private test evidence and public delivery

Real browser sessions, messages, account content, app screens, device dumps and
logs are private by default. Keep them in ignored local runs/private archives;
permission to test an app is not permission to publish its data. Do not open or
capture personal apps for routine acceptance: use synthetic fixture apps/data.
If a real-app check is necessary, explain its scope and keep captures private.
Public UI references require inspected synthetic content and explicit review.
Never move private screenshots into GitHub issues, PRs, releases or CI artifacts.

Public automation uploads only its current host run after both repository-path
and actual-input privacy checks. Rejection fails packaging/upload; it does not
redact bytes silently or count the run as verified. The guard rejects raw tracked
testresults, capture/device paths and common media/archive signatures. This is a
bounded backstop, not semantic detection of all private text or encoded content.
Safe-looking filenames and hashes do not establish permission to publish.
Routine [host CI](../.github/workflows/quality.yml) checks its current raw directory
before generic evidence packing and artifact upload. It does not run the release
archive-member privacy check. [Release tooling](../tools/release.py) checks current
host input before sealing; its validate/export/publish path repeats the shared
path/signature policy over integrity-verified archive members, reading bounded
uncompressed prefixes without extraction. Private local archive tooling retains
its general integrity scope.

Privacy removal overrides historical-evidence retention. Record withdrawal and
availability honestly; retained bytes still require their original hashes.
Do not copy removed captures into public backups or manufacture replacement
passing evidence. Local private copies remain until separately deleted by owner.

For exposure: remove public artifacts/assets, prepare a fresh filtered clone,
verify every exposed branch/tag, obtain two fresh approvals and request the
specific history/protection exception. Rewriting hashes invalidates old reviews
and source/report bindings: disclose that, never invent retroactive approvals.
Pause tag-triggered releases during approved replacement, restore protections,
then verify remote refs and public artifacts. GitHub Support must handle cached
commit/PR references; other clones must be cleaned or replaced. Never merge old
history back into the sanitized repository.

## Publication boundary

```mermaid
flowchart TB
    Device[Real app and device capture] --> Private[Ignored private local evidence]
    Private --> Access[Authorized local reviewer access only]
    Fixture[Reviewed synthetic public references] --> Source[Safe source and summaries]
    Source --> Host[Current host run]
    Host --> Guard[Indexed paths and public input privacy guard]
    Guard -->|Routine CI pass| Pack[Generic evidence pack and integrity check]
    Pack --> Artifact[Upload routine current-run artifact]
    Guard -->|Release build pass| Seal[Seal release host archive]
    Seal --> Members[Verify archive integrity then member privacy]
    Members -->|Pass| Release[Export or publish release evidence]
    Guard -->|Reject| Block[Fail job and withhold upload]
    Members -->|Reject| Block
    Withdraw[Privacy removal request] --> Notice[Explicit unavailable evidence notice]
```

No new cloud service or paid monitoring is introduced.

```mermaid
sequenceDiagram
    participant Test as Device tester
    participant Local as Ignored private storage
    participant Git as Candidate and pre-push gate
    participant CI as Host workflow
    participant Rel as Release tools
    participant Guard as Shared privacy guard
    participant GH as GitHub storage
    Test->>Local: Capture personal app only when necessary
    Note over Local,GH: No automatic transfer of private device evidence
    Git->>Git: Reject indexed or pushed raw evidence paths
    Git->>CI: Reviewed safe source
    alt Routine host CI
        CI->>Guard: Current run directory
        alt Safe input
            Guard-->>CI: Permit packing
            CI->>CI: Generic evidence pack and integrity check
            CI->>GH: Upload routine current-run artifact
        else Capture, device dump or nested archive
            Guard-->>CI: Fail job
            Note over CI,GH: Artifact upload is withheld
        end
    else Release build and later delivery
        CI->>Rel: Current release host results
        Rel->>Guard: Uncompressed current-host input
        alt Safe input
            Guard-->>Rel: Permit sealing
            Rel->>Rel: Seal release archive and verify integrity
            Note over Rel,Guard: Release validation before export or publication
            Rel->>Guard: Verified member paths and uncompressed prefixes
            alt Safe archive members
                Guard-->>Rel: Permit release delivery
                Rel->>GH: Publish release evidence when authorized
            else Forbidden member or capture/archive signature
                Guard-->>Rel: Fail validation
                Note over Rel,GH: Export and publication are withheld
            end
        else Capture, device dump or nested archive
            Guard-->>Rel: Fail build
            Note over Rel,GH: Release packaging is withheld
        end
    end
```
