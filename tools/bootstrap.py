"""Initialize a generated project or apply authorized GitHub protection explicitly."""

import argparse
import json
import re
import subprocess

import project


def initialize(root, name, repository):
    config = project.read_json(root / "project.json")
    config.update(name=name, repository=repository)
    project.validate(config)
    project.write_json(root / "project.json", config)
    record = root / "reviews/approvals.json"
    project.write_json(record, {"schema_version": 1, "candidate_sha256": None, "reviews": []})
    print("Initialized project configuration. Obtain fresh reviews before pushing these changes.")


def check_repository(root, repository):
    if project.load(root)["repository"].casefold() != repository.casefold():
        raise ValueError("Repository identity mismatch; initialize this generated project first")


def protect(root):
    config = project.load(root)
    repository = config["repository"]
    actual = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if (
        actual.returncode
        or json.loads(actual.stdout).get("nameWithOwner", "").casefold() != repository.casefold()
    ):
        raise ValueError(
            "Configured repository does not match this checkout's GitHub remote; initialize first"
        )
    payload = project.read_json(root / "config/github/main-protection.json")
    existing = subprocess.run(
        ["gh", "api", f"repos/{repository}/branches/main/protection", "--include"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if existing.returncode == 0:
        raise ValueError(
            "Main is already protected; preserve existing rules and reconcile explicitly. No settings changed."
        )
    status = re.search(r"(?m)^HTTP/\S+\s+(\d{3})\b", existing.stdout)
    if not status or status[1] != "404":
        raise ValueError("Cannot confirm unprotected main: " + existing.stderr.strip())
    result = subprocess.run(
        [
            "gh",
            "api",
            "--method",
            "PUT",
            f"repos/{repository}/branches/main/protection",
            "--input",
            "-",
        ],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode:
        raise ValueError("GitHub protection not applied: " + result.stderr.strip())
    state = json.loads(result.stdout)
    checks = state.get("required_status_checks", {})
    if (
        not state.get("enforce_admins", {}).get("enabled")
        or not checks.get("strict")
        or checks.get("checks") != payload["required_status_checks"]["checks"]
        or state.get("required_pull_request_reviews") is None
        or state.get("allow_force_pushes", {}).get("enabled") is not False
        or state.get("allow_deletions", {}).get("enabled") is not False
        or not state.get("required_conversation_resolution", {}).get("enabled")
    ):
        raise ValueError("GitHub response did not confirm strict administrator enforcement")
    print(
        f"Applied protected main to {repository}; verify repository plan/permissions and current host checks."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--name", required=True)
    init.add_argument("--repository", required=True)
    sub.add_parser(
        "protect", help="Requires authorization to change configured repository settings"
    )
    check = sub.add_parser(
        "check", help="Verify actual CI repository matches initialized configuration"
    )
    check.add_argument("--repository", required=True)
    args = parser.parse_args()
    if args.command == "init":
        initialize(project.ROOT, args.name, args.repository)
    elif args.command == "protect":
        protect(project.ROOT)
    else:
        check_repository(project.ROOT, args.repository)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        raise SystemExit(str(error)) from error
