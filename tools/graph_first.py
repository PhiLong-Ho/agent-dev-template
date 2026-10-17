"""Portable Claude/Codex graph-first hook and bounded navigation CLI."""

import argparse
from contextlib import closing, contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import sqlite3
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from graph_common import CODE, fingerprint, inventory, read_json, repo_root, write_json

HERE = Path(__file__).resolve().parent
GUIDE = "Graph-first: consult code-review-graph before coding/review; use query or impact commands from the graph-first skill. Graph hits are navigation hints, not exhaustive literal matches. Graphify is a release snapshot only; never run graphify update/watch or install its git hooks. For UI work reconcile latest approved references before final review."


def cache_for(root):
    base = Path(os.environ.get("GRAPH_FIRST_HOME", Path.home() / ".cache/agent-graph-first"))
    key = hashlib.sha256(os.path.normcase(str(root.resolve())).encode()).hexdigest()[:24]
    return base / key


@contextmanager
def locked(cache):
    cache.mkdir(parents=True, exist_ok=True)
    with (cache / "lock").open("a+b") as stream:
        stream.seek(0)
        if stream.seek(0, os.SEEK_END) == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            if os.name == "nt":
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def refresh(root, cache):
    records = inventory(root)
    digest = fingerprint(records)
    marker = cache / "fresh.json"
    if (
        marker.exists()
        and (cache / "graph.db").exists()
        and read_json(marker).get("fingerprint") == digest
    ):
        return records
    marker.unlink(missing_ok=True)
    write_json(cache / "inputs.json", records)
    runtime = HERE / "runtime.json"
    if not runtime.exists():
        runtime = Path.home() / ".local/share/agent-graph-first/runtime.json"
    settings = read_json(runtime) if runtime.exists() else {}
    worker_python = settings.get("crg_python", sys.executable)
    environment = dict(os.environ, CRG_SERIAL_PARSE="1", CRG_PARSE_WORKERS="1", PYTHONUTF8="1")
    result = subprocess.run(
        [
            worker_python,
            "-I",
            str(HERE / "graph_worker.py"),
            str(root),
            str(cache),
            str(cache / "inputs.json"),
        ],
        capture_output=True,
        timeout=8,
        env=environment,
    )
    (cache / "refresh.log").write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise ValueError("code-review-graph refresh failed; inspect " + str(cache / "refresh.log"))
    summary = json.loads(result.stdout)
    if inventory(root) != records:
        raise ValueError("Source changed during graph refresh; retry")
    write_json(marker, {"fingerprint": digest, "root": str(root), **summary})
    return records


def query(cache, text, paths=(), scope=None):
    database = cache / "graph.db"
    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True, timeout=0.25)) as db:
        # Bound VM work too, including corrupt/very large third-party graphs.
        ticks = [0]

        def budget():
            ticks[0] += 1
            return int(ticks[0] > 2000)

        db.set_progress_handler(budget, 1000)
        if paths:
            rows = []
            for path in list(paths)[:8]:
                rows += db.execute(
                    "SELECT kind,name,file_path,line_start,qualified_name FROM nodes WHERE file_path=? LIMIT 5",
                    (path,),
                ).fetchall()
        else:
            escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            sql = "SELECT kind,name,file_path,line_start,qualified_name FROM nodes WHERE name LIKE ? ESCAPE '\\'"
            values = ["%" + escaped[:120] + "%"]
            if scope:
                prefix = str(scope).replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
                sql += " AND (file_path=? OR file_path LIKE ? ESCAPE '\\')"
                values += [str(scope), prefix + ("\\\\" if os.sep == "\\" else "/") + "%"]
            rows = db.execute(sql + " LIMIT 5", values).fetchall()
        lines = []
        for kind, name, path, line, qualified in rows[:8]:
            lines.append(f"[crg] {kind} {name} -> {path}:{line or 1}")
            related = db.execute(
                "SELECT kind,source_qualified,target_qualified FROM edges WHERE source_qualified=? OR target_qualified=? LIMIT 4",
                (qualified, qualified),
            ).fetchall()
            lines += [f"  {edge}: {source} -> {target}" for edge, source, target in related]
        return "\n".join(lines)[:5000]


def search_request(payload, root):
    name, inp = payload.get("tool_name", ""), payload.get("tool_input", {})
    if not isinstance(inp, dict):
        return None
    if name == "Grep":
        # Only redirect a bare symbol search. Exact options retain tool semantics.
        redirect = not bool(set(inp) - {"pattern", "path"})
        pattern, target = inp.get("pattern", ""), inp.get("path", ".")
    elif name in {"Bash", "PowerShell", "exec_command"}:
        command = inp.get("command", inp.get("cmd", ""))
        if not isinstance(command, str):
            return None
        command = command.strip()
        if not re.match(r"^(?:rg|grep|ripgrep)(?:\s|$)", command) or any(
            c in command for c in "|;&`\n\r$"
        ):
            return None
        lexer = shlex.shlex(command, posix=False)
        lexer.whitespace_split = True
        lexer.commenters = "#"
        parts = list(lexer)
        # Non-POSIX tokenization keeps PowerShell/Windows path separators. Strip
        # only whole-token quotes; complex shell escapes stay outside redirection.
        parts = [
            part[1:-1] if len(part) >= 2 and part[0] == part[-1] and part[0] in "\"'" else part
            for part in parts
        ]
        # Single, simple search only: don't suppress a pipeline or side effects.
        if not parts or parts[0] not in {"rg", "grep", "ripgrep"}:
            return None
        # Backslash targets are ambiguous between PowerShell and Git Bash on
        # Windows. Supply graph hints, but preserve the original tool execution.
        redirect = "\\" not in command
        while len(parts) > 1 and parts[1] in {
            "-n",
            "--line-number",
            "-i",
            "--ignore-case",
            "--no-heading",
            "-l",
            "--files-with-matches",
            "-F",
            "--fixed-strings",
        }:
            redirect = False
            parts.pop(1)
        if len(parts) not in (2, 3):
            return None
        if any(c in command for c in "|;&`\n\r$"):
            return None
        if re.search(r"(?:^|\s)#\s*--graph-tried(?:\s|$)", command):
            return None
        pattern, target = parts[1], parts[2] if len(parts) == 3 else "."
    else:
        return None
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{2,100}", pattern):
        return None
    cwd = Path(payload.get("cwd", root))
    if isinstance(inp.get("workdir"), str):
        cwd = Path(inp["workdir"])
    target = Path(target)
    target = (cwd / target).resolve() if not target.is_absolute() else target.resolve()
    if not target.is_relative_to(root):
        return None
    if target.suffix:
        if target.suffix.lower() not in CODE:
            return None
        redirect = False
    return pattern, redirect, target


def context(event, message, deny=False):
    output = {"hookEventName": event, "additionalContext": message[:6500]}
    if deny:
        output.update(permissionDecision="deny", permissionDecisionReason=message[:6500])
    return {"hookSpecificOutput": output}


def changed_paths(root):
    from graph_common import git

    return [
        str(root / path)
        for path in git(root, "diff", "--name-only", "HEAD", "-z").split("\0")
        if path
    ][:8]


def handle(payload):
    event = payload.get("hook_event_name", "PreToolUse")
    if event == "SessionStart":
        return context(event, GUIDE)
    if event not in {"PreToolUse", "UserPromptSubmit", "Stop"}:
        return {}
    root = repo_root(payload.get("cwd", os.getcwd()))
    request = search_request(payload, root) if event == "PreToolUse" else None
    pattern, redirect, scope = request if request else (None, False, None)
    editing = payload.get("tool_name") in {"apply_patch", "Edit", "Write", "MultiEdit"}
    if event == "PreToolUse" and not pattern and not editing:
        return {}
    cache = cache_for(root)
    with locked(cache):
        refresh(root, cache)
        if event == "Stop":
            return {}  # Never ask the agent to continue from Stop.
        if not pattern:
            result = query(cache, "", changed_paths(root)) if changed_paths(root) else ""
            return context(
                event,
                GUIDE
                + (
                    "\nCurrent change impact (bounded direct neighbors):\n" + result
                    if result
                    else "\nCRG refreshed; no indexed changed-file context."
                ),
            )
        result = query(cache, pattern, scope=scope)
        if not result:
            return context(event, "CRG has no symbol match; original search may proceed.")
        session = hashlib.sha256(str(payload.get("session_id", "unknown")).encode()).hexdigest()[
            :24
        ]
        state_path = cache / ("session-" + session + ".json")
        state = read_json(state_path) if state_path.exists() else {}
        previous = state.get(pattern, 0)
        state[pattern] = previous + 1
        state = dict(list(state.items())[-128:])
        write_json(state_path, state)
        message = f"Fresh code-review-graph navigation for {pattern}:\n{result}\nFor exhaustive/literal results retry the shell search with the comment # --graph-tried (not a CLI flag), use precise Grep options, or retry once. Graph matches are hints, not completeness proof."
        # First hit teaches without blocking. At most one denial per query/session.
        return context(event, message, deny=redirect and previous == 1 and "session_id" in payload)


def safe_handle(payload):
    try:
        return handle(payload)
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
        sqlite3.Error,
        subprocess.SubprocessError,
    ) as error:
        event = payload.get("hook_event_name", "PreToolUse")
        if event == "Stop":
            return {}
        return context(
            event,
            "Graph-first fallback: "
            + str(error)[:500]
            + ". Continue with scoped source reads/search; graph freshness is unverified.",
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["hook", "query", "impact", "refresh"])
    parser.add_argument("terms", nargs="*")
    args = parser.parse_args()
    if args.command == "hook":
        try:
            payload = json.loads(sys.stdin.buffer.read(1024 * 1024).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Hook payload must be an object")
            print(json.dumps(safe_handle(payload)))
        except (ValueError, TypeError):
            print("{}")
    else:
        root = repo_root(Path.cwd())
        cache = cache_for(root)
        with locked(cache):
            records = refresh(root, cache)
            paths = (
                [str((root / term).resolve()) for term in args.terms]
                if args.command == "impact"
                else ()
            )
            print(
                query(cache, " ".join(args.terms), paths)
                if args.command != "refresh"
                else f"CRG current: {len(records)} eligible files; {cache}"
            )


if __name__ == "__main__":
    main()
