"""Explicit graph input policy shared by hooks and release snapshots (stdlib only)."""

import fnmatch
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys

CODE = set(
    ".py .java .kt .kts .js .jsx .ts .tsx .mjs .cjs .go .rs .c .h .cpp .hpp .cs .rb .php .swift .scala .sh .ps1 .sql .dart .vue .svelte .gradle .xml .html .css .scss .json .toml .yaml .yml .properties .ini".split()
)
DOCS = {".md", ".rst", ".txt", ".adoc"}
NAMES = {
    "Makefile",
    "Dockerfile",
    "Justfile",
    ".gitignore",
    ".gitattributes",
    ".graphignore",
    "pre-push",
    "pre-commit",
    "post-commit",
    "post-checkout",
}
BLOCKED = set(
    ".git .local .codex .claude .idea .vscode .venv venv node_modules vendor build dist target artifacts testresults reviews screenshots screenshot ui-reference __pycache__ .gradle .cache .pytest_cache .ruff_cache graphify-out .code-review-graph .graph-first".split()
)
SECRET = (
    ".env*",
    "secrets.*",
    "credentials.*",
    "*.credentials.*",
    "auth.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "*.lock",
    "token.json",
    "tokens.json",
    "local.properties",
    "settings.local.*",
    "config.local.*",
    "*.min.js",
    "*.min.css",
    "*.generated.*",
)
MAX_FILE = 2 * 1024 * 1024
MAX_TOTAL = 40 * 1024 * 1024
MAX_FILES = 5000


def tool_python(distribution, expected):
    """Resolve and verify an installed tool without downloading or running repo code."""
    code = "from importlib.metadata import version; import sys; print(version(sys.argv[1]))"
    candidates = [Path(sys.executable)]
    try:
        directory = Path(
            subprocess.check_output(["uv", "tool", "dir"], timeout=10, text=True).strip()
        )
        candidates.append(
            directory
            / distribution
            / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        )
    except (OSError, subprocess.SubprocessError):
        pass
    for candidate in candidates:
        if not candidate.is_file():
            continue
        result = subprocess.run(
            [str(candidate), "-I", "-c", code, distribution],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip() == expected:
            return str(candidate)
    raise ValueError(f"Install tested {distribution}=={expected} with pip or uv tool install")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def git(root, *args):
    return subprocess.check_output(
        ["git", *args], cwd=root, timeout=5, stderr=subprocess.PIPE
    ).decode("utf-8")


def repo_root(cwd):
    return Path(git(cwd, "rev-parse", "--show-toplevel").strip()).resolve()


def eligible(name, documents=False, extra=()):
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
        return False
    if any(part.lower() in BLOCKED for part in path.parts):
        return False
    if any(fnmatch.fnmatchcase(path.name.lower(), pattern) for pattern in SECRET):
        return False
    if any(fnmatch.fnmatchcase(name, pattern) for pattern in extra):
        return False
    return path.name in NAMES or path.suffix.lower() in (CODE | DOCS if documents else CODE)


def read_source(path):
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_FILE + 1)
    if len(data) > MAX_FILE:
        raise ValueError("Graph input budget exceeded")
    if b"\0" in data:
        raise ValueError("Binary content in graph text input")
    data.decode("utf-8")
    return data


def inventory(root, documents=False, tracked=False):
    root = Path(root).resolve()
    policy = root / ".graphignore"
    extra = []
    if policy.is_file() and not policy.is_symlink():
        extra = [
            line.strip()
            for line in policy.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
    args = ["ls-files", "--cached", "-z"]
    if not tracked:
        args += ["--others", "--exclude-standard"]
    records, total = {}, 0
    for name in sorted(set(git(root, *args).split("\0"))):
        if not name or not eligible(name, documents, extra):
            continue
        path = root / name
        if not path.is_file():
            continue
        # Reject symlinks at any depth, including a linked parent folder.
        if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
            raise ValueError(f"Graph input is linked: {name}")
        if not path.resolve().is_relative_to(root):
            raise ValueError("Graph input escaped repository")
        size = path.stat().st_size
        total += size
        if size > MAX_FILE or total > MAX_TOTAL or len(records) >= MAX_FILES:
            raise ValueError("Graph input budget exceeded; narrow .graphignore")
        data = read_source(path)
        if b"\0" in data:
            raise ValueError(f"Binary content in graph text input: {name}")
        data.decode("utf-8")
        records[name] = hashlib.sha256(data).hexdigest()
    return records


def fingerprint(records):
    return hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()
