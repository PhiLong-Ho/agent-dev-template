"""Explicit, backed-up user hook/skill installation for Claude and Codex."""

import argparse
import hashlib
from datetime import datetime, timezone
import json
import os
import stat
import tempfile
from pathlib import Path
import shlex
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
START = "<!-- agent-graph-first:start -->"
END = "<!-- agent-graph-first:end -->"


def backup_name(path):
    return (
        path.parent.name
        + "-"
        + path.name
        + "-"
        + hashlib.sha256(str(path).encode()).hexdigest()[:12]
    )


def replace(path, data, backups):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == data:
        return
    mode = 0o600
    if path.exists():
        if path.is_symlink():
            raise ValueError("Refusing to replace linked user configuration")
        mode = stat.S_IMODE(path.stat().st_mode)
        backups.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(backups, 0o700)
        descriptor = os.open(
            backups / backup_name(path),
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0),
            0o600,
        )
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(path.read_bytes())
    # NamedTemporaryFile creates an exclusive private file; neither the backup
    # nor replacement is ever temporarily opened with umask-derived public modes.
    with tempfile.NamedTemporaryFile(
        prefix=".graph-first-", dir=path.parent, delete=False
    ) as stream:
        temporary = Path(stream.name)
        stream.write(data)
    try:
        os.chmod(temporary, mode)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def merged_hooks(settings, command, windows_command=None):
    if not isinstance(settings, dict):
        raise ValueError("Settings must be a JSON object")
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("Hooks must be an event object")
    for groups in hooks.values():
        if not isinstance(groups, list) or any(
            not isinstance(group, dict)
            or not isinstance(group.get("hooks"), list)
            or any(not isinstance(handler, dict) for handler in group["hooks"])
            for group in groups
        ):
            raise ValueError("Invalid existing hook groups; original settings preserved")
    # Migrate only the recognized legacy entries, preserving every other handler.
    for event, groups in list(hooks.items()):
        retained = []
        for group in groups:
            group = dict(group)
            group["hooks"] = [
                h
                for h in group.get("hooks", [])
                if not (
                    h.get("type") == "command"
                    and (
                        "agent-graph-first/graph_first.py"
                        in h.get("command", "").replace("\\", "/")
                        or h.get("command", "").strip() == "code-review-graph update"
                        or ".claude/scripts/smart-grep-hook.sh"
                        in h.get("command", "").replace("\\", "/")
                    )
                )
            ]
            if group["hooks"]:
                retained.append(group)
        if retained:
            hooks[event] = retained
        else:
            hooks.pop(event, None)
    for event in ("SessionStart", "UserPromptSubmit", "PreToolUse", "Stop"):
        group = {"hooks": [{"type": "command", "command": command, "timeout": 20}]}
        if windows_command:
            group["hooks"][0]["commandWindows"] = windows_command
        if event == "PreToolUse":
            group["matcher"] = "^(Bash|PowerShell|Grep|apply_patch|Edit|Write|MultiEdit)$"
        hooks.setdefault(event, []).append(group)
    return settings


def instructions(previous, block):
    if START in previous:
        if previous.count(START) != 1 or previous.count(END) != 1:
            raise ValueError("Malformed existing graph-first instruction block")
        before, tail = previous.split(START)
        _, after = tail.split(END)
        return before.rstrip() + ("\n\n" if before.strip() else "") + block + after
    return previous.rstrip() + ("\n\n" if previous.strip() else "") + block + "\n"


def discover_python():
    from graph_common import tool_python

    return tool_python("code-review-graph", "2.3.6")


def install(home, crg_python):
    home = Path(home).resolve()
    runtime = home / ".local/share/agent-graph-first"
    backups = (
        runtime
        / "backups"
        / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8])
    )
    version = subprocess.check_output(
        [
            str(crg_python),
            "-I",
            "-c",
            "from importlib.metadata import version; print(version('code-review-graph'))",
        ],
        text=True,
        timeout=10,
    ).strip()
    if version != "2.3.6":
        raise ValueError("Expected tested code-review-graph 2.3.6, got " + version)
    # Parse all existing JSON before any writes; malformed user settings are preserved.
    targets = [home / ".claude/settings.json", home / ".codex/hooks.json"]
    configs = [json.loads(p.read_text(encoding="utf-8")) if p.exists() else {} for p in targets]
    argv = [Path(sys.executable).as_posix(), "-I", (runtime / "graph_first.py").as_posix(), "hook"]
    command = shlex.join(argv)
    windows_command = "& " + " ".join("'" + arg.replace("'", "''") + "'" for arg in argv)

    policy = (
        START
        + "\nUse the graph-first skill automatically for coding and code review. Hooks refresh code-review-graph and provide bounded navigation/impact. Query the graph before broad source search, then verify actual source/tests. Failed/stale/missing graphs permit diagnosed scoped fallback; # --graph-tried is a shell comment, never a flag. Graphify is refreshed ONLY by the release build from curated code/docs; do not install graphify git hooks or run watch/update during development. UI changes must reconcile the latest approved per-screen/state reference catalog with actual renders and reviewer approval, retaining historical evidence externally.\n"
        + END
    )
    instruction_paths = [home / ".claude/CLAUDE.md", home / ".codex/AGENTS.md"]
    texts = [
        instructions(p.read_text(encoding="utf-8") if p.exists() else "", policy)
        for p in instruction_paths
    ]
    configs = [
        merged_hooks(config, command, windows_command if path.parent.name == ".codex" else None)
        for path, config in zip(targets, configs)
    ]
    for name in ("graph_first.py", "graph_common.py", "graph_worker.py"):
        replace(runtime / name, (HERE / name).read_bytes(), backups)
    replace(
        runtime / "runtime.json",
        (json.dumps({"crg_python": str(Path(crg_python).resolve())}, indent=2) + "\n").encode(),
        backups,
    )
    for path, config in zip(targets, configs):
        replace(path, (json.dumps(config, indent=2) + "\n").encode(), backups)
    for path, text in zip(instruction_paths, texts):
        replace(path, text.encode("utf-8"), backups)
    skill = (HERE.parent / ".agents/skills/graph-first/SKILL.md").read_text(encoding="utf-8")
    for client in (".claude", ".codex"):
        invocation = (
            windows_command.removesuffix(" 'hook'")
            if client == ".codex" and sys.platform == "win32"
            else command.removesuffix(" hook")
        )
        installed_skill = skill.replace("python tools/graph_first.py", invocation)
        if client == ".codex" and sys.platform == "win32":
            installed_skill = installed_skill.replace("```sh", "```powershell")
        replace(
            home / client / "skills/graph-first/SKILL.md", installed_skill.encode("utf-8"), backups
        )
    return {
        "runtime": str(runtime),
        "backups": str(backups),
        "activation": "Restart Claude/Codex sessions. In Codex /hooks review and trust the installed definitions; trust was not bypassed.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--crg-python", type=Path)
    args = parser.parse_args()
    print(json.dumps(install(args.home, args.crg_python or discover_python()), indent=2))


if __name__ == "__main__":
    main()
