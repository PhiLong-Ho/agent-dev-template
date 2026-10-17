"""Run inside the pinned code-review-graph environment; never execute project code."""

import json
from pathlib import Path
import sys
from importlib.metadata import version

sys.path.insert(0, str(Path(__file__).resolve().parent))

from graph_common import read_json, read_source


def run(root, cache, manifest):
    if version("code-review-graph") != "2.3.6":
        raise ValueError("Expected tested code-review-graph 2.3.6")
    from code_review_graph.graph import GraphStore
    from code_review_graph.parser import CodeParser
    from code_review_graph.search import rebuild_fts_index

    import hashlib

    root, cache = Path(root), Path(cache)
    parser = CodeParser(root)
    records = read_json(manifest)
    parsed, unsupported = 0, []
    with GraphStore(cache / "graph.db") as store:
        expected = {str(root / name) for name in records}
        for name in store.get_all_files():
            if name not in expected:
                store.remove_file_data(name)
        store.commit()
        for name, digest in records.items():
            path = root / name
            if parser.detect_language(path) is None:
                unsupported.append(name)
                continue
            data = read_source(path)
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError("Source changed during graph refresh")
            old = store.get_nodes_by_file(str(path))
            if old and old[0].file_hash == digest:
                continue
            nodes, edges = parser.parse_bytes(path, data)
            store.store_file_nodes_edges(str(path), nodes, edges, digest)
            parsed += 1
        rebuild_fts_index(store)
        store.commit()
    return {"parsed": parsed, "unsupported": unsupported}


if __name__ == "__main__":
    print(json.dumps(run(*sys.argv[1:])))
