"""Release-only Graphify AST extraction plus deterministic document navigation."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
from urllib.parse import unquote
import zipfile

from graph_common import DOCS, git, inventory, read_json, read_source, tool_python, write_json


SCOPE = "Graphify local AST + file inventory + explicit document headings/links. No LLM semantic extraction; unsupported AST formats retain file nodes. Evidence, local/secret config, binaries/screenshots and generated/vendor files excluded."


def document_index(graph, root, records):
    """Index explicit headings/relative links only: no semantic inference claims."""
    nodes, edges = graph.setdefault("nodes", []), graph.setdefault("edges", [])
    for node in list(nodes):
        source = node.get("source_file")
        if source in records:
            edges.append(
                {
                    "source": "file:" + source,
                    "target": node["id"],
                    "relation": "contains",
                    "source_file": source,
                    "confidence": "EXTRACTED",
                    "weight": 1.0,
                }
            )
    for name in records:
        nodes.append(
            {
                "id": "file:" + name,
                "label": name,
                "source_file": name,
                "file_type": "document" if Path(name).suffix.lower() in DOCS else "code",
                "extraction": "file-inventory",
            }
        )
    for name in records:
        if Path(name).suffix.lower() not in DOCS:
            continue
        text = (root / name).read_text(encoding="utf-8")
        for line, content in enumerate(text.splitlines(), 1):
            match = re.match(r"^#{1,6}\s+(.+)", content)
            if match:
                ident = f"doc:{name}#L{line}"
                nodes.append(
                    {
                        "id": ident,
                        "label": match[1][:300],
                        "source_file": name,
                        "source_location": str(line),
                        "file_type": "document",
                        "extraction": "explicit-heading",
                    }
                )
                edges.append(
                    {
                        "source": "file:" + name,
                        "target": ident,
                        "relation": "contains",
                        "source_file": name,
                        "confidence": "EXTRACTED",
                        "weight": 1.0,
                    }
                )
        for link in re.findall(r"\]\(<?([^\s)>]+)>?(?:\s[^)]*)?\)", text):
            link = unquote(link.split("#")[0])
            if not link or ":" in link or link.startswith("/"):
                continue
            target = (root / PurePosixPath(name).parent / link).resolve()
            if target.is_relative_to(root) and target.relative_to(root).as_posix() in records:
                edges.append(
                    {
                        "source": "file:" + name,
                        "target": "file:" + target.relative_to(root).as_posix(),
                        "relation": "links_to",
                        "source_file": name,
                        "confidence": "EXTRACTED",
                        "weight": 1.0,
                    }
                )


def normalize(value, snapshot):
    if isinstance(value, str):
        return (
            value.replace(str(snapshot) + "/", "")
            .replace(str(snapshot) + "\\", "")
            .replace(snapshot.as_posix() + "/", "")
        )
    if isinstance(value, list):
        return [normalize(item, snapshot) for item in value]
    if isinstance(value, dict):
        return {key: normalize(item, snapshot) for key, item in value.items()}
    return value


def create(root, output, tag, source_commit):
    root, output = Path(root).resolve(), Path(output)
    if (
        git(root, "status", "--porcelain").strip()
        or git(root, "rev-parse", "HEAD").strip() != source_commit
    ):
        raise ValueError("Graphify release requires the clean current source commit")
    if git(root, "rev-parse", f"{tag}^{{commit}}").strip() != source_commit:
        raise ValueError("Graphify tag/source mismatch")
    records = inventory(root, documents=True, tracked=True)
    if not records:
        raise ValueError("No eligible release graph inputs")
    output.mkdir(parents=True, exist_ok=True)
    archive = output / "knowledge-graph.zip"
    if archive.exists():
        raise ValueError("Refusing to overwrite a release graph")
    executable = tool_python("graphifyy", "0.9.16")
    with tempfile.TemporaryDirectory(prefix="release-graph-") as directory:
        snapshot = Path(directory).resolve()
        for name, digest in records.items():
            data = read_source(root / name)
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError("Release graph input changed")
            target = snapshot / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        result = subprocess.run(
            [
                executable,
                "-I",
                "-m",
                "graphify",
                "extract",
                str(snapshot),
                "--code-only",
                "--no-cluster",
                "--max-workers",
                "1",
            ],
            capture_output=True,
            timeout=300,
        )
        (output / "graphify.log").write_bytes(result.stdout + result.stderr)
        if result.returncode:
            raise ValueError("Graphify release extraction failed; inspect graphify.log")
        graph = normalize(read_json(snapshot / "graphify-out/graph.json"), snapshot)
        document_index(graph, root, records)
        if inventory(root, documents=True, tracked=True) != records:
            raise ValueError("Source changed while creating release graph")
        manifest = {
            "schema_version": 1,
            "source_commit": source_commit,
            "tag": tag,
            "graphify_version": "0.9.16",
            "scope": SCOPE,
            "files": records,
            "ast_files": sorted(
                {
                    node.get("source_file")
                    for node in graph["nodes"]
                    if node.get("_origin") == "ast" and node.get("source_file") in records
                }
            ),
            "document_files": sorted(name for name in records if Path(name).suffix.lower() in DOCS),
        }
        write_json(output / "knowledge-graph-manifest.json", manifest)
        encoded = (json.dumps(graph, indent=2) + "\n").encode("utf-8")
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            bundle.writestr("graph.json", encoded)
            bundle.write(output / "knowledge-graph-manifest.json", "manifest.json")
    return manifest


def validate(archive, manifest_path, source_commit, tag, records):
    manifest = read_json(manifest_path)
    if (
        manifest.get("schema_version") != 1
        or manifest.get("graphify_version") != "0.9.16"
        or manifest.get("scope") != SCOPE
    ):
        raise ValueError("Release knowledge graph schema/tool/scope mismatch")
    if manifest.get("document_files") != sorted(
        name for name in records if Path(name).suffix.lower() in DOCS
    ):
        raise ValueError("Release knowledge graph document scope mismatch")
    if (
        manifest.get("source_commit") != source_commit
        or manifest.get("tag") != tag
        or manifest.get("files") != records
    ):
        raise ValueError("Release knowledge graph source/input binding mismatch")
    with zipfile.ZipFile(archive) as bundle:
        if (
            sorted(bundle.namelist()) != ["graph.json", "manifest.json"]
            or bundle.read("manifest.json") != Path(manifest_path).read_bytes()
        ):
            raise ValueError("Invalid knowledge graph archive")
        graph = json.loads(bundle.read("graph.json"))
        ast_files = sorted(
            {
                node.get("source_file")
                for node in graph["nodes"]
                if node.get("_origin") == "ast" and node.get("source_file") in records
            }
        )
        if manifest.get("ast_files") != ast_files:
            raise ValueError("Release knowledge graph AST scope mismatch")
        for item in graph["nodes"] + graph["edges"]:
            if item.get("source_file") and item["source_file"] not in records:
                raise ValueError("Knowledge graph contains an excluded or unrelated source")
        file_nodes = {
            node["source_file"]
            for node in graph["nodes"]
            if node.get("extraction") == "file-inventory"
        }
        if file_nodes != set(records):
            raise ValueError("Knowledge graph file coverage mismatch")
