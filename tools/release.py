"""Build/report/seal current evidence, then validate before any release mutation."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

import evidence
import graph_release
from graph_common import inventory
import project
import quality
import review_gate

REPORTS = ("release-report.md", "release-report.json")
EVIDENCE = ("release-evidence.zip", "release-evidence.json")


def notes(root, version):
    text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    marker = f"## [{version}]"
    matches = [section for section in text.split("\n## ") if section.startswith(f"[{version}]")]
    if len(matches) != 1 or not matches[0].partition("\n")[2].strip():
        raise ValueError(f"Missing or ambiguous changelog section {marker}")
    return "## " + matches[0].strip() + "\n"


def context(root, tag, workflow_url):
    config = project.load(root)
    if tag != "v" + config["version"]:
        raise ValueError("Tag/project version mismatch")
    if (
        not workflow_url.startswith(f"https://github.com/{config['repository']}/actions/runs/")
        or not workflow_url.rsplit("/", 1)[-1].isdigit()
    ):
        raise ValueError("Expected current repository Actions run URL")
    state = project.source_state(root)
    if state["dirty"] or state["commit"] == "uncommitted-bootstrap":
        raise ValueError("Release requires a clean committed source tree")
    if project.git(root, "rev-parse", f"{tag}^{{commit}}") != state["commit"]:
        raise ValueError("Tag does not identify current source")
    review_gate.check(root, "HEAD")
    return config, state


def build(root, output, tag, workflow_url):
    config, state = context(root, tag, workflow_url)
    changes = notes(root, config["version"])
    output.mkdir(parents=True, exist_ok=False)
    raw = output / "raw"
    host = quality.run(root, raw)
    if not host["passed"]:
        raise ValueError("Current host checks failed; raw evidence retained")
    builds = project.execute(
        root,
        config["release"]["build"],
        raw / "build-logs",
        output=(output / "build").resolve(),
        version=config["version"],
    )
    project.write_json(raw / "build-results.json", builds)
    if any(item["exit_code"] for item in builds):
        raise ValueError("Release build failed; raw evidence retained")
    if project.source_state(root) != state:
        raise ValueError("Release build modified source")
    assets = set()
    for pattern in config["release"]["artifacts"]:
        matching = list((output / "build").glob(pattern))
        if not matching:
            raise ValueError(f"Missing release artifact: {pattern}")
        for path in matching:
            if (
                path.is_symlink()
                or not path.is_file()
                or path.parent.resolve() != (output / "build").resolve()
            ):
                raise ValueError("Invalid release artifact")
            evidence.safe_name(path.name)
            if path.name in {
                *REPORTS,
                *EVIDENCE,
                "package.json",
                "SHA256SUMS.txt",
                "release-notes.md",
                "knowledge-graph.zip",
                "knowledge-graph-manifest.json",
                "graphify.log",
            }:
                raise ValueError("Release artifact name collides with metadata")
            assets.add(path.name)
            shutil.copyfile(path, output / path.name)
    if config["release"].get("knowledge_graph", False):
        graph_release.create(root, output, tag, state["commit"])
        assets.update({"knowledge-graph.zip", "knowledge-graph-manifest.json"})
        shutil.copyfile(output / "graphify.log", raw / "graphify.log")
    tests = host["tests"]
    executed = sum(value for key, value in tests.items() if key != "skipped")
    coverage = project.read_json(root / "docs/requirements.json")
    report = {
        "schema_version": 1,
        "name": config["name"],
        "version": config["version"],
        "tag": tag,
        "repository": config["repository"],
        "source_commit": state["commit"],
        "workflow_url": workflow_url,
        "tests": tests,
        "executed_denominator": executed,
        "pass_rate": tests["passed"] / executed,
        "coverage": dict(Counter(req["coverage"] for req in coverage["requirements"])),
        "gaps": [
            {"id": req["id"], "gap": req["gap"]}
            for req in coverage["requirements"]
            if req["coverage"] != "mapped"
        ],
        "knowledge_graph": config["release"].get("knowledge_graph", False),
        "scope": host["scope"],
        "host_results_sha256": evidence.digest_file(raw / "host-results.json"),
        "test_sources": {name: evidence.digest_file(raw / name) for name in config["test_results"]},
        "coverage_snapshot_sha256": evidence.digest_file(root / "docs/coverage-snapshot.json"),
    }
    base = f"https://github.com/{config['repository']}"
    markdown = render_report(report)
    project.write_json(output / REPORTS[1], report)
    (output / REPORTS[0]).write_text(markdown, encoding="utf-8", newline="\n")
    for name in REPORTS:
        shutil.copyfile(output / name, raw / name)
    shutil.copyfile(root / "docs/coverage-snapshot.json", raw / "coverage-snapshot.json")
    archive_context = {
        "scope": host["scope"],
        "source_commit": state["commit"],
        "tag": tag,
        "repository": config["repository"],
        "workflow_url": workflow_url,
    }
    descriptor = evidence.create_archive(raw, output / "archive", archive_context)
    shutil.copyfile(output / "archive/evidence.zip", output / EVIDENCE[0])
    descriptor.update(
        archive=EVIDENCE[0],
        storage={
            "kind": "github-release-target",
            "url": f"{base}/releases/download/{tag}/{EVIDENCE[0]}",
            "availability": "Pending successful authorized publication; target is not upload confirmation",
        },
    )
    project.write_json(output / EVIDENCE[1], descriptor)
    (output / "release-notes.md").write_text(
        changes + f"\n[Release report]({base}/releases/download/{tag}/release-report.md)\n",
        encoding="utf-8",
        newline="\n",
    )
    names = assets | set(REPORTS) | set(EVIDENCE) | {"release-notes.md"}
    metadata = {
        "schema_version": 1,
        "tag": tag,
        "version": config["version"],
        "repository": config["repository"],
        "workflow_url": workflow_url,
        "source": state,
        "files": {name: evidence.digest_file(output / name) for name in sorted(names)},
    }
    project.write_json(output / "package.json", metadata)
    (output / "SHA256SUMS.txt").write_text(
        "".join(
            f"{evidence.digest_file(output / name)}  {name}\n"
            for name in sorted(names | {"package.json"})
        ),
        encoding="utf-8",
        newline="\n",
    )
    validate(root, output)
    print("PASS release package, report, evidence and source bindings")


def render_report(report):
    base = f"https://github.com/{report['repository']}"
    tag = report["tag"]
    graph = (
        f"\n[Knowledge graph]({base}/releases/download/{tag}/knowledge-graph.zip) - local AST + explicit document headings/links, no semantic inference.\n"
        if report.get("knowledge_graph")
        else ""
    )
    return (
        f"# {report['name']} {report['version']} release report\n\nSource: `{report['source_commit']}`.\n\n[Changelog]({base}/blob/{tag}/CHANGELOG.md) · [Release]({base}/releases/tag/{tag}) · [Workflow]({report['workflow_url']}) · [Raw evidence]({base}/releases/download/{tag}/release-evidence.zip)\n\nTests: {report['tests']}; pass rate {report['tests']['passed']}/{report['executed_denominator']} executed cases ({report['pass_rate']:.1%}); skipped excluded from denominator.\n\nRequirement mappings: {report['coverage']}. Mapping is not scenario execution.\n\nScope: {report['scope']}\n\nGaps:\n"
        + "\n".join(f"- {gap['id']}: {gap['gap']}" for gap in report["gaps"])
        + "\n"
        + graph
    )


def validate(root, output):
    metadata = project.read_json(output / "package.json")
    config, state = context(root, metadata["tag"], metadata["workflow_url"])
    if (
        metadata.get("schema_version") != 1
        or metadata["source"] != state
        or metadata["repository"] != config["repository"]
        or metadata["version"] != config["version"]
    ):
        raise ValueError("Release source/identity mismatch")
    files = metadata["files"]
    required = {*REPORTS, *EVIDENCE, "release-notes.md"}
    if config["release"].get("knowledge_graph", False):
        required.update({"knowledge-graph.zip", "knowledge-graph-manifest.json"})
    if not required < files.keys():
        raise ValueError("Missing artifacts/report/evidence")
    expected = dict(files, **{"package.json": evidence.digest_file(output / "package.json")})
    seen = {}
    for line in (output / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        evidence.safe_name(name)
        if (
            "/" in name
            or (output / name).is_symlink()
            or name in seen
            or name not in expected
            or digest != expected[name]
            or evidence.digest_file(output / name) != digest
        ):
            raise ValueError("Release checksum mismatch")
        seen[name] = digest
    if seen != expected:
        raise ValueError("Release checksums incomplete")
    if config["release"].get("knowledge_graph", False):
        graph_release.validate(
            output / "knowledge-graph.zip",
            output / "knowledge-graph-manifest.json",
            state["commit"],
            metadata["tag"],
            inventory(root, documents=True, tracked=True),
        )
    descriptor = project.read_json(output / EVIDENCE[1])
    manifest = evidence.verify_archive(output / EVIDENCE[0], descriptor)
    for key in ("tag", "repository", "workflow_url"):
        if manifest["context"].get(key) != metadata[key]:
            raise ValueError("Archive metadata mismatch")
    if manifest["context"].get("source_commit") != state["commit"]:
        raise ValueError("Archive source mismatch")
    report = project.read_json(output / REPORTS[1])
    for key in ("tag", "version", "repository", "workflow_url"):
        if report.get(key) != metadata[key]:
            raise ValueError("Report metadata mismatch")
    if (
        report.get("schema_version") != 1
        or report.get("name") != config["name"]
        or report.get("source_commit") != state["commit"]
    ):
        raise ValueError("Report identity mismatch")
    if report.get("knowledge_graph", False) != config["release"].get("knowledge_graph", False):
        raise ValueError("Report knowledge graph scope mismatch")
    if (output / REPORTS[0]).read_text(encoding="utf-8") != render_report(report):
        raise ValueError("Markdown report differs from structured report")
    with zipfile.ZipFile(output / EVIDENCE[0]) as bundle:
        for name in REPORTS:
            if bundle.read("data/" + name) != (output / name).read_bytes():
                raise ValueError("Archived report mismatch")
        host_bytes = bundle.read("data/host-results.json")
        host = json.loads(host_bytes)
        if (
            not host.get("passed")
            or host["source"] != state
            or hashlib.sha256(host_bytes).hexdigest() != report["host_results_sha256"]
            or report["tests"] != host["tests"]
        ):
            raise ValueError("Current host outcome mismatch")
        if set(report["test_sources"]) != set(config["test_results"]):
            raise ValueError("Missing configured test sources")
        counts = quality.count_results(
            [json.loads(bundle.read("data/" + name)) for name in config["test_results"]],
            state["commit"],
        )
        executed = sum(value for key, value in counts.items() if key != "skipped")
        if (
            counts != report["tests"]
            or not executed
            or not counts["passed"]
            or any(counts[key] for key in ("failed", "error", "unexpected_success"))
            or report["executed_denominator"] != executed
            or report["pass_rate"] != counts["passed"] / executed
        ):
            raise ValueError("Actual test counts/rate mismatch")
        if (
            host.get("source_unchanged") is not True
            or report["scope"] != host["scope"]
            or not host["validation"]
            or not host["commands"]
            or any(item["exit_code"] for item in host["validation"] + host["commands"])
        ):
            raise ValueError("Host commands failed or incomplete")
        if json.loads(bundle.read("data/source.json")) != state:
            raise ValueError("Raw source identity mismatch")
        builds = json.loads(bundle.read("data/build-results.json"))
        if not builds or any(item["exit_code"] for item in builds):
            raise ValueError("Release build did not pass")
        for name, digest in report["test_sources"].items():
            evidence.safe_name(name)
            if hashlib.sha256(bundle.read("data/" + name)).hexdigest() != digest:
                raise ValueError("Raw test source mismatch")
        if hashlib.sha256(bundle.read("data/coverage-snapshot.json")).hexdigest() != report[
            "coverage_snapshot_sha256"
        ] or report["coverage_snapshot_sha256"] != evidence.digest_file(
            root / "docs/coverage-snapshot.json"
        ):
            raise ValueError("Coverage source mismatch")
    requirements = project.read_json(root / "docs/requirements.json")["requirements"]
    if report["coverage"] != dict(Counter(req["coverage"] for req in requirements)) or report[
        "gaps"
    ] != [
        {"id": req["id"], "gap": req["gap"]} for req in requirements if req["coverage"] != "mapped"
    ]:
        raise ValueError("Requirement coverage/gaps mismatch")
    expected_notes = notes(root, config["version"])
    if not (output / "release-notes.md").read_text(encoding="utf-8").startswith(expected_notes):
        raise ValueError("Changelog notes mismatch")
    return metadata


def publish(root, output):
    metadata = validate(root, output)  # All local validation precedes any GitHub call.
    repository, tag = metadata["repository"], metadata["tag"]
    existing = subprocess.run(
        ["gh", "api", f"repos/{repository}/releases?per_page=100", "--paginate", "--slurp"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    matches = [
        release
        for page in json.loads(existing.stdout)
        for release in page
        if release.get("tag_name") == tag
    ]
    if matches:
        raise ValueError(
            "Release already exists; use a new version (including after a partial draft)"
        )
    assets = [
        str(output / name)
        for name in sorted(set(metadata["files"]) | {"package.json", "SHA256SUMS.txt"})
    ]
    subprocess.run(
        [
            "gh",
            "release",
            "create",
            tag,
            *assets,
            "--repo",
            repository,
            "--verify-tag",
            "--draft",
            "--title",
            f"{project.load(root)['name']} {metadata['version']}",
            "--notes-file",
            str(output / "release-notes.md"),
        ],
        check=True,
    )
    subprocess.run(
        ["gh", "release", "edit", tag, "--repo", repository, "--draft=false"], check=True
    )
    print(f"Published https://github.com/{repository}/releases/tag/{tag}")


def export_package(root, output, destination):
    metadata = validate(root, output)
    destination.mkdir(parents=True, exist_ok=False)
    for name in sorted(set(metadata["files"]) | {"package.json", "SHA256SUMS.txt"}):
        shutil.copyfile(output / name, destination / name)
    validate(root, destination)
    print("PASS exact validated publication set exported without intermediate directories")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "verify", "export", "publish"])
    parser.add_argument("--output", type=Path, default=project.ROOT / "artifacts/release")
    parser.add_argument("--tag")
    parser.add_argument("--workflow-url")
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    if args.command == "build":
        if not args.tag or not args.workflow_url:
            parser.error("build requires --tag and --workflow-url")
        build(project.ROOT, args.output, args.tag, args.workflow_url)
    elif args.command == "verify":
        validate(project.ROOT, args.output)
    elif args.command == "export":
        if not args.destination:
            parser.error("export requires --destination")
        export_package(project.ROOT, args.output, args.destination)
    else:
        publish(project.ROOT, args.output)


if __name__ == "__main__":
    try:
        main()
    except (
        ValueError,
        OSError,
        KeyError,
        TypeError,
        subprocess.CalledProcessError,
        zipfile.BadZipFile,
    ) as error:
        raise SystemExit(f"FAIL {error}") from error
