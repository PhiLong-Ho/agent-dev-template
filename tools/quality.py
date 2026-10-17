"""Run actual configured gates, retaining raw outcomes even when a command fails."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

import check_privacy
import check_docs
import check_requirements
import coverage
import project


def count_results(documents, source_commit):
    counts = dict.fromkeys(
        ("passed", "failed", "error", "skipped", "expected_failure", "unexpected_success"), 0
    )
    seen = set()
    for data in documents:
        if data.get("schema_version") != 1 or data.get("source_commit") != source_commit:
            raise ValueError("Test schema/source mismatch")
        if not isinstance(data.get("cases"), list) or not data["cases"]:
            raise ValueError("Missing or empty test outcomes")
        for case in data["cases"]:
            ident, status = case.get("id"), case.get("status")
            if (
                not isinstance(ident, str)
                or not ident.strip()
                or ident in seen
                or status not in counts
            ):
                raise ValueError("Invalid or duplicate test outcome")
            seen.add(ident)
            counts[status] += 1
    return counts


def test_counts(folder, result_files, source_commit):
    return count_results([project.read_json(folder / name) for name in result_files], source_commit)


def run(root, folder):
    config = project.load(root)
    folder.mkdir(parents=True, exist_ok=False)
    before = project.source_state(root)
    project.write_json(folder / "source.json", before)
    validation = []
    for name, operation in [
        (
            "requirements",
            lambda: check_requirements.validate(
                project.read_json(root / "docs/requirements.json"), root
            ),
        ),
        ("privacy", lambda: check_privacy.repository_errors(root)),
        ("coverage", lambda: coverage.check(root)),
        ("documentation", lambda: check_docs.validate(root)),
    ]:
        try:
            errors = operation()
            if errors:
                raise ValueError("\n".join(errors))
            validation.append({"name": name, "exit_code": 0})
        except (ValueError, OSError, KeyError, SyntaxError) as error:
            validation.append({"name": name, "exit_code": 1, "error": str(error)})
    outcomes = project.execute(
        root,
        config["commands"],
        folder,
        evidence=folder.resolve(),
        monitor_context={
            "source_commit": before["commit"],
            "source_content_sha256": hashlib.sha256(
                json.dumps(before["files"], sort_keys=True).encode()
            ).hexdigest(),
        },
    )
    report = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": before,
        "validation": validation,
        "commands": outcomes,
        "scope": "Configured host gates only. Unrun E2E/device/visual/performance checks are unverified.",
    }
    try:
        report["tests"] = test_counts(folder, config["test_results"], before["commit"])
        report["source_unchanged"] = project.source_state(root)["files"] == before["files"]
        report["passed"] = (
            report["source_unchanged"]
            and all(item["exit_code"] == 0 for item in validation + outcomes)
            and not any(report["tests"][key] for key in ("failed", "error", "unexpected_success"))
            and report["tests"]["passed"] > 0
        )
    except (ValueError, OSError, KeyError, TypeError) as error:
        report.update(passed=False, result_error=str(error))
    project.write_json(folder / "host-results.json", report)
    print(
        "PASS host gates" if report["passed"] else "FAIL host gates; inspect retained logs/results"
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    config = project.load()
    folder = args.evidence or project.ROOT / "testresults" / config[
        "version"
    ] / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ-host")
    return int(not run(project.ROOT, folder)["passed"])


if __name__ == "__main__":
    sys.exit(main())
