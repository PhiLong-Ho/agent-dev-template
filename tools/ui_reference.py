"""Check latest explicitly approved UI renders against relevant current sources."""

import argparse
import fnmatch
import hashlib
from pathlib import Path
import re
import struct
import zlib

from graph_common import git, read_json


def source_hashes(root, patterns):
    names = set(
        git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0")
    )
    selected = {}
    for pattern in patterns:
        if not isinstance(pattern, str) or pattern.startswith("/") or ".." in Path(pattern).parts:
            raise ValueError("UI source pattern must stay inside repository")
        matched = [
            name
            for name in names
            if name and fnmatch.fnmatchcase(name, pattern) and (root / name).is_file()
        ]
        if not matched:
            raise ValueError("UI source pattern matches no current files: " + pattern)
        for name in matched:
            path = root / name
            if path.is_symlink() or not path.resolve().is_relative_to(root):
                raise ValueError("Linked UI source")
            selected[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return selected


def png_size(data):
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("UI references must be real PNG captures")
    offset, size, ended, pixels = 8, None, False, False
    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        body = data[offset + 8 : offset + 8 + length]
        crc = data[offset + 8 + length : offset + 12 + length]
        if len(crc) != 4 or zlib.crc32(kind + body) != struct.unpack(">I", crc)[0]:
            raise ValueError("Corrupt UI reference PNG")
        if kind == b"IHDR":
            size = struct.unpack(">II", body[:8])
        if kind == b"IDAT":
            pixels = True
        if kind == b"IEND":
            ended = True
        offset += 12 + length
    if not size or not all(size) or not ended or not pixels:
        raise ValueError("Incomplete UI reference PNG")
    return list(size)


def validate(root):
    root = Path(root).resolve()
    catalog = read_json(root / "docs/ui-reference/catalog.json")
    if catalog.get("schema_version") != 1:
        raise ValueError("Unknown UI catalog schema")
    if catalog.get("mode") == "no-ui":
        if (
            catalog.get("entries")
            or catalog.get("source_patterns")
            or catalog.get("required_states")
            or catalog.get("source_hashes")
            or not catalog.get("reason", "").strip()
        ):
            raise ValueError("No-UI scope needs reason and empty sources/entries")
        return
    if (
        catalog.get("mode") != "ui"
        or not catalog.get("source_patterns")
        or not catalog.get("required_states")
    ):
        raise ValueError("UI catalog requires sources and required states")
    current = source_hashes(root, catalog["source_patterns"])
    if catalog.get("source_hashes") != current:
        raise ValueError(
            "UI references stale: inspect fresh renders and reconcile approval/source hashes"
        )
    entries = catalog.get("entries", [])
    seen = set()
    for entry in entries:
        key = entry["state"]
        if key in seen:
            raise ValueError("Duplicate UI reference state")
        seen.add(key)
        name = entry["image"]
        path = root / "docs/ui-reference" / name
        if (
            Path(name).is_absolute()
            or ".." in Path(name).parts
            or path.is_symlink()
            or not path.resolve().is_relative_to(root / "docs/ui-reference")
        ):
            raise ValueError("Unsafe UI reference path")
        data = path.read_bytes()
        if (
            hashlib.sha256(data).hexdigest() != entry["sha256"]
            or png_size(data) != entry["dimensions"]
        ):
            raise ValueError("UI reference image changed or dimensions mismatch")
        if (
            not entry.get("reviewer", "").strip()
            or not entry.get("evidence", "").strip()
            or not entry.get("configuration", "").strip()
            or not re.fullmatch(
                r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|\+00:00)",
                entry.get("approved_at", ""),
            )
        ):
            raise ValueError("UI reference lacks actual approval/evidence/configuration")
    if seen != set(catalog["required_states"]):
        raise ValueError("Missing or unexpected required UI reference states")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "fingerprint"])
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.command == "check":
        validate(root)
        print(
            "PASS current UI reference scope and integrity (approval attestation, not automated visual judgment)"
        )
    else:
        import json

        print(
            json.dumps(
                source_hashes(
                    root, read_json(root / "docs/ui-reference/catalog.json")["source_patterns"]
                ),
                indent=2,
            )
        )
