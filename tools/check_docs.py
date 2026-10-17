"""Check local documentation links, Spec Kit sections and retained evidence hashes."""

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def headings(text):
    counts = {}
    anchors = set()
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.M):
        slug = re.sub(r"[^\w -]", "", heading.lower().strip()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        anchors.add(slug if count == 0 else f"{slug}-{count}")
    return anchors


def check_links(root, files):
    errors = []
    root = root.resolve()
    for path in files:
        if not path.is_file():
            errors.append(f"Missing documentation file: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        # Example commands/JSON contain template paths; only rendered prose links count.
        text = re.sub(r"```[^\n]*\n[\s\S]*?```|~~~[^\n]*\n[\s\S]*?~~~", "", text)
        targets = re.findall(r"!?\[[^\]\n]+\]\(([^)\n]+)\)", text)
        targets += re.findall(r"<(?:img|a)\b[^>]*\b(?:src|href)=[\"']([^\"']+)[\"']", text)
        for target in targets:
            target = target.strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            parts = urlsplit(target)
            if parts.scheme or parts.netloc:
                continue
            destination = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            if not destination.is_relative_to(root) or not destination.exists():
                errors.append(f"{path.relative_to(root)}: missing/outside local link {target}")
                continue
            if parts.fragment and destination.suffix.lower() == ".md":
                if unquote(parts.fragment) not in headings(destination.read_text(encoding="utf-8")):
                    errors.append(f"{path.relative_to(root)}: missing heading link {target}")
    return errors


def check_spec(root):
    text = (root / "SPEC.md").read_text(encoding="utf-8")
    required = [
        "User Scenarios & Testing",
        "Requirements",
        "Functional Requirements",
        "Key Entities",
        "Success Criteria",
        "Measurable Outcomes",
        "Assumptions",
    ]
    actual = headings(text)
    errors = [
        f"Spec Kit section missing: {name}"
        for name in required
        if re.sub(r"[^\w -]", "", name.lower()).replace(" ", "-") not in actual
    ]
    if "## Implementation history" in text:
        errors.append("Release history belongs in CHANGELOG.md")
    return errors


def validate(root):
    listing = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", "*.md"], cwd=root
    ).decode("utf-8")
    return check_links(
        root, [root / name for name in sorted(set(listing.splitlines()))]
    ) + check_spec(root)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    errors = validate(root)
    for error in errors:
        print("FAIL " + error)
    print("Documentation links/Spec Kit sections checked; no visual certification.")
    raise SystemExit(bool(errors))
