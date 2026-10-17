"""Shared project configuration, portable commands and source provenance."""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import run_monitor

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def validate(config):
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported project configuration")
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,99}", config.get("name", "")):
        raise ValueError("Invalid project name")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", config.get("repository", "")):
        raise ValueError("Expected owner/repository")
    if not re.fullmatch(
        r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", config.get("version", "")
    ):
        raise ValueError("Use a stable MAJOR.MINOR.PATCH version")
    for commands in (config.get("commands"), config.get("release", {}).get("build")):
        if not isinstance(commands, list) or not commands:
            raise ValueError("At least one quality/build command required")
        names = set()
        for command in commands:
            name, argv = command.get("name"), command.get("argv")
            if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9-]+", name) or name in names:
                raise ValueError("Unique portable command names required")
            names.add(name)
            if (
                not isinstance(argv, list)
                or not argv
                or any(not isinstance(a, str) or not a for a in argv)
            ):
                raise ValueError("Commands must be nonempty argument arrays")
            for key, default in (("timeout_seconds", 900), ("idle_warning_seconds", 60)):
                value = command.get(key, default)
                if not isinstance(value, (int, float)):
                    raise ValueError(f"{key} must be a number")
                run_monitor.positive(value)
    for key, entries in (
        ("test_results", config.get("test_results")),
        ("artifacts", config["release"].get("artifacts")),
    ):
        if not isinstance(entries, list) or not entries or len(set(entries)) != len(entries):
            raise ValueError(f"Nonempty distinct {key} required")
        for entry in entries:
            if (
                not isinstance(entry, str)
                or not entry
                or any(c in entry for c in "\\/:")
                or entry in {".", ".."}
            ):
                raise ValueError(f"{key} must be filenames/globs within their output folder")
    return config


def load(root=ROOT):
    return validate(read_json(root / "project.json"))


def git(root, *args):
    result = subprocess.run(["git", *args], cwd=root, capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout.decode("utf-8").strip()


def source_state(root):
    files = (
        subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root
        )
        .decode("utf-8")
        .split("\0")
    )
    records = []
    for name in sorted(set(files)):
        if not name or name.startswith(("testresults/", "reviews/")):
            continue
        path = root / name
        if path.is_file():
            if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
                raise ValueError("Source provenance does not accept links")
            records.append({"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    if not records:
        raise ValueError("No source files")
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True
    )
    head = revision.stdout.strip() if revision.returncode == 0 else ""
    return {
        "commit": head or "uncommitted-bootstrap",
        "dirty": bool(git(root, "status", "--porcelain")),
        "files": records,
    }


def execute(root, commands, folder, *, monitor_context=None, **values):
    folder.mkdir(parents=True, exist_ok=True)
    values["python"] = sys.executable
    outcomes = []
    monitor = run_monitor.Session(
        folder / "monitor",
        context=monitor_context or {"scope": "configured commands; source binding not supplied"},
    )
    print(f'Monitor: python tools/run_monitor.py watch "{monitor.folder}"', flush=True)
    try:
        for command in commands:
            argv = command["argv"][:]
            for key, value in values.items():
                argv = [argument.replace("{" + key + "}", str(value)) for argument in argv]
            log = folder / (command["name"] + ".log")
            result = monitor.run(
                argv,
                cwd=root,
                label=(
                    command["name"]
                    if re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}", command["name"])
                    else f"command-{len(outcomes) + 1}"
                ),
                timeout=command.get("timeout_seconds", 900),
                idle_warning=command.get("idle_warning_seconds", 60),
                combined_path=log,
                extractor=run_monitor.AssertionProgress(),
            )
            code = result.returncode
            outcomes.append(
                {
                    "name": command["name"],
                    "argv": argv,
                    "exit_code": code,
                    "log": log.name,
                    "state": result.state,
                    "duration_seconds": result.duration_seconds,
                    "monitor_error": result.error,
                }
            )
            print(f"{command['name']}: exit {code}", flush=True)
            if result.state == "cancelled" or monitor.error:
                break
    except BaseException:
        monitor.failed = True
        raise
    finally:
        final = monitor.finish()
    if outcomes and (
        monitor.error or (final != "completed" and not any(row["exit_code"] for row in outcomes))
    ):
        # Host/release consumers use exit_code. Retain the actual child result
        # while making a final monitor fault authoritative for acceptance.
        last = outcomes[-1]
        last["monitor_error"] = monitor.error or "monitor_finalization_failed"
        if last["exit_code"] == 0:
            last.update(child_exit_code=0, exit_code=74, state="failed")
    return outcomes
