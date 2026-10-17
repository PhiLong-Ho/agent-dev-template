"""Observable hooks, real graph tools, curated releases and UI reference gates."""

from contextlib import closing
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import struct
import stat
import zlib
import subprocess
import tempfile
import unittest
from unittest import mock
import zipfile

import graph_common as common
import graph_first as hook
import graph_release
import install_graph_first as installer
import project
import ui_reference


class RepoCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        for args in (
            ("init", "-q"),
            ("config", "user.name", "Fixture"),
            ("config", "user.email", "fixture@example.invalid"),
        ):
            self.git(*args)
        self.put(".gitignore", "artifacts/\n.local/\n")

    def git(self, *args):
        return common.git(self.root, *args).strip()

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")


class GraphPolicyTests(RepoCase):
    def test_only_eligible_tracked_code_documents_enter_release(self):
        for name in (
            "src/app.py",
            "project.json",
            ".github/workflows/build.yml",
            "src/token_parser.py",
            "docs/guide.md",
            "testresults/1/log.md",
            "screenshots/view.py",
            ".claude/local.md",
            "build/generated.py",
            "src/secrets.py",
            "docs/view.png",
            "vendor/pkg/code.java",
        ):
            self.put(name, "# fixture\n")
        self.commit()
        self.put("src/new.py", "# untracked\n")
        self.put(".local/ignored.py", "# ignored\n")
        self.assertEqual(
            set(common.inventory(self.root, documents=True, tracked=True)),
            {
                ".gitignore",
                "src/app.py",
                "project.json",
                ".github/workflows/build.yml",
                "src/token_parser.py",
                "docs/guide.md",
            },
        )
        self.assertIn("src/new.py", common.inventory(self.root))
        self.assertNotIn("docs/guide.md", common.inventory(self.root))

    def test_extra_exclusions_and_budget_fail_without_reading_binary_as_code(self):
        self.put("src/app.py", "pass\n")
        self.put(".graphignore", "src/app.py\n")
        self.assertEqual(set(common.inventory(self.root)), {".gitignore", ".graphignore"})
        self.put(".graphignore", "")
        with mock.patch.object(common, "MAX_FILE", 1):
            with self.assertRaisesRegex(ValueError, "budget"):
                common.inventory(self.root)
        (self.root / "src/app.py").write_bytes(b"\0binary")
        with self.assertRaisesRegex(ValueError, "Binary"):
            common.inventory(self.root)

    def test_path_traversal_and_nested_noise_are_never_eligible(self):
        for name in (
            "../escape.py",
            "/absolute.py",
            "C:/private.py",
            "x\\private.py",
            "a/node_modules/pkg.py",
            "a/TESTRESULTS/log.md",
        ):
            self.assertFalse(common.eligible(name, documents=True))


class HookTests(RepoCase):
    def setUp(self):
        super().setUp()
        self.put("src/app.py", "def navigate():\n    pass\n")
        self.commit()
        self.cache = self.root / "artifacts/cache"
        self.cache.mkdir(parents=True)
        with closing(sqlite3.connect(self.cache / "graph.db")) as db:
            db.executescript(
                "CREATE TABLE nodes(kind,name,file_path,line_start,qualified_name); CREATE TABLE edges(kind,source_qualified,target_qualified);"
            )
            db.execute(
                "INSERT INTO nodes VALUES(?,?,?,?,?)",
                ("Function", "navigate", str(self.root / "src/app.py"), 1, "app.navigate"),
            )
            db.execute("INSERT INTO edges VALUES(?,?,?)", ("CALLS", "app.navigate", "app.render"))
            db.commit()
        self.payload = {
            "hook_event_name": "PreToolUse",
            "cwd": str(self.root),
            "session_id": "real-fixture-session",
            "tool_name": "Bash",
            "tool_input": {"command": "rg navigate src"},
        }

    def run_hook(self, payload=None):
        with (
            mock.patch.object(hook, "cache_for", return_value=self.cache),
            mock.patch.object(hook, "refresh", return_value={}) as refresh,
        ):
            result = hook.safe_handle(payload or self.payload)
            return result, refresh.call_count

    def test_first_hit_teaches_second_redirects_once_then_retry_is_allowed(self):
        for count in range(3):
            result, _ = self.run_hook()
            output = result["hookSpecificOutput"]
            self.assertEqual(output.get("permissionDecision"), "deny" if count == 1 else None)
            self.assertIn("app.py:1", output["additionalContext"])
            self.assertIn("CALLS", output["additionalContext"])
        independent = dict(self.payload, session_id="another-session")
        self.assertNotIn("permissionDecision", self.run_hook(independent)[0]["hookSpecificOutput"])

    def test_override_literal_complex_noncode_and_cross_repo_searches_proceed(self):
        for command in (
            "rg navigate src # --graph-tried",
            "rg 'nav.*' src",
            "rg navigate src | sort",
            "rg navigate src; echo side-effect",
            "rg navigate docs/guide.md",
            "rg navigate ..",
            "rg --files",
            "python script.py",
            'python -c "unterminated',
            "@'\nprint(\"coding script\")\n'@ | python -",
            "rg 'x# --graph-tried' src",
        ):
            payload = copy.deepcopy(self.payload)
            payload["tool_input"]["command"] = command
            if "guide.md" in command:
                self.put("docs/guide.md", "navigate")
            with self.subTest(command=command):
                result, calls = self.run_hook(payload)
                self.assertEqual(result, {})
                self.assertEqual(calls, 0)

    def test_windows_backslash_paths_never_redirect_to_conflicting_directory(self):
        good = self.put("src/nested/good.py", "def navigate():\n    pass\n")
        bad = self.put("srcnested/unrelated.py", "def navigate():\n    pass\n")
        self.put("src/nested space/good.py", "def navigate():\n    pass\n")
        with closing(sqlite3.connect(self.cache / "graph.db")) as db:
            db.execute("DELETE FROM nodes")
            for path in (good, bad, self.root / "src/nested space/good.py"):
                db.execute(
                    "INSERT INTO nodes VALUES(?,?,?,?,?)",
                    ("Function", "navigate", str(path), 1, str(path)),
                )
            db.commit()
        targets = [
            r"src\nested",
            r".\src\nested",
            str(good.parent).replace("/", "\\"),
            r'"src\nested space"',
        ]
        for index, target in enumerate(targets):
            payload = copy.deepcopy(self.payload)
            payload["session_id"] = "windows-path-" + str(index)
            payload["tool_input"]["command"] = "rg navigate " + target
            for _ in range(3):
                result, _ = self.run_hook(payload)
                serialized = json.dumps(result)
                self.assertNotIn("unrelated.py", serialized)
                if os.name == "nt":
                    self.assertIn("good.py", serialized)
                self.assertNotIn("permissionDecision", serialized)

    def test_hits_outside_requested_directory_do_not_redirect_search(self):
        self.put("other/code.py", "# target outside source directory\n")
        payload = copy.deepcopy(self.payload)
        payload["tool_input"]["command"] = "rg navigate other"
        for _ in range(3):
            result, _ = self.run_hook(payload)
            output = result["hookSpecificOutput"]
            self.assertNotIn("permissionDecision", output)
            self.assertIn("no symbol match", output["additionalContext"])

    def test_common_search_options_keep_results_and_add_graph_context(self):
        for command in ("rg -n navigate src", "rg -F navigate src", "rg navigate src/app.py"):
            payload = copy.deepcopy(self.payload)
            payload["tool_input"]["command"] = command
            for _ in range(3):
                result, calls = self.run_hook(payload)
                self.assertEqual(calls, 1)
                self.assertNotIn("permissionDecision", result["hookSpecificOutput"])
                self.assertIn("app.py:1", result["hookSpecificOutput"]["additionalContext"])

    def test_claude_grep_and_codex_edit_and_prompt_use_shared_context(self):
        grep = dict(
            self.payload, tool_name="Grep", tool_input={"pattern": "navigate", "path": "src"}
        )
        self.assertIn("navigate", self.run_hook(grep)[0]["hookSpecificOutput"]["additionalContext"])
        self.put("src/app.py", "def navigate():\n    return 1\n")
        for event, name in (
            ("UserPromptSubmit", ""),
            ("PreToolUse", "apply_patch"),
            ("PreToolUse", "Edit"),
        ):
            result, calls = self.run_hook(dict(self.payload, hook_event_name=event, tool_name=name))
            self.assertEqual(calls, 1)
            self.assertIn("app.py:1", result["hookSpecificOutput"]["additionalContext"])

    def test_misses_and_timeout_or_lock_failure_allow_diagnosed_fallback(self):
        payload = copy.deepcopy(self.payload)
        payload["tool_input"]["command"] = "rg absent src"
        result, _ = self.run_hook(payload)
        self.assertNotIn("permissionDecision", result["hookSpecificOutput"])
        for failure in (
            ValueError("stale"),
            subprocess.TimeoutExpired("worker", 8),
            OSError("locked"),
            sqlite3.DatabaseError("corrupt"),
        ):
            with (
                mock.patch.object(hook, "refresh", side_effect=failure),
                mock.patch.object(hook, "cache_for", return_value=self.cache),
            ):
                result = hook.safe_handle(self.payload)["hookSpecificOutput"]
                self.assertNotIn("permissionDecision", result)
                self.assertIn("fallback", result["additionalContext"])
        with mock.patch.object(hook, "cache_for", return_value=self.cache), hook.locked(self.cache):
            result = hook.safe_handle(self.payload)["hookSpecificOutput"]
            self.assertNotIn("permissionDecision", result)

    def test_stop_never_requests_continuation_and_unknown_session_never_denies(self):
        stop = dict(self.payload, hook_event_name="Stop", stop_hook_active=True)
        self.assertEqual(self.run_hook(stop)[0], {})
        missing = dict(self.payload)
        del missing["session_id"]
        for _ in range(3):
            self.assertNotIn("permissionDecision", self.run_hook(missing)[0]["hookSpecificOutput"])


class InstalledGraphTests(RepoCase):
    def test_real_crg_refresh_observes_edits_deletions_and_test_relationships(self):
        self.put(
            "src/app.py", "def navigate():\n    return 1\ndef render():\n    return navigate()\n"
        )
        self.put(
            "tests/test_app.py",
            "from src.app import navigate\ndef test_navigation():\n    assert navigate() == 1\n",
        )
        self.commit()
        runtime = self.root / "artifacts/runtime"
        runtime.mkdir(parents=True)
        for name in ("graph_first.py", "graph_common.py", "graph_worker.py"):
            shutil.copyfile(project.ROOT / "tools" / name, runtime / name)
        common.write_json(runtime / "runtime.json", {"crg_python": installer.discover_python()})
        cache = self.root / "artifacts/cache"
        cache.mkdir()
        with mock.patch.object(hook, "HERE", runtime):
            hook.refresh(self.root, cache)
            result = hook.query(cache, "navigate")
            self.assertIn("app.py:1", result)
            self.assertIn("render", result)
            self.assertIn("TESTED_BY", result)
            self.put("src/app.py", "def updated():\n    return 2\n")
            hook.refresh(self.root, cache)
            self.assertNotIn("app.py:1", hook.query(cache, "navigate"))
            self.assertIn("updated", hook.query(cache, "updated"))
            (self.root / "src/app.py").unlink()
            hook.refresh(self.root, cache)
            self.assertEqual(hook.query(cache, "updated"), "")

    def test_real_graphify_release_contains_code_docs_links_and_provenance(self):
        self.put("src/app.py", "def navigate():\n    return 1\n")
        self.put("docs/guide.md", "# Navigation\n[Code](../src/app.py)\n")
        self.put("testresults/1/log.md", "# excluded\n")
        self.put(".claude/private.md", "# excluded\n")
        self.commit()
        self.git("tag", "v0.1.0")
        sha = self.git("rev-parse", "HEAD")
        output = self.root / "artifacts/release"
        manifest = graph_release.create(self.root, output, "v0.1.0", sha)
        self.assertEqual(set(manifest["files"]), {".gitignore", "src/app.py", "docs/guide.md"})
        graph_release.validate(
            output / "knowledge-graph.zip",
            output / "knowledge-graph-manifest.json",
            sha,
            "v0.1.0",
            manifest["files"],
        )
        with zipfile.ZipFile(output / "knowledge-graph.zip") as bundle:
            graph = json.loads(bundle.read("graph.json"))
        self.assertTrue(any(n.get("label") == "navigate()" for n in graph["nodes"]))
        self.assertTrue(
            any(
                n.get("extraction") == "explicit-heading" and n["label"] == "Navigation"
                for n in graph["nodes"]
            )
        )
        self.assertTrue(any(e.get("relation") == "links_to" for e in graph["edges"]))
        graph_path = self.root / "artifacts/query/graph.json"
        common.write_json(graph_path, graph)
        result = subprocess.run(
            [
                common.tool_python("graphifyy", "0.9.16"),
                "-I",
                "-m",
                "graphify",
                "query",
                "Navigation",
                "--graph",
                str(graph_path),
                "--budget",
                "1500",
            ],
            capture_output=True,
            timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertIn("src/app.py", result.stdout.decode("utf-8"))
        route = subprocess.run(
            [
                common.tool_python("graphifyy", "0.9.16"),
                "-I",
                "-m",
                "graphify",
                "path",
                "Navigation",
                "navigate()",
                "--graph",
                str(graph_path),
            ],
            capture_output=True,
            timeout=20,
        )
        self.assertEqual(route.returncode, 0, route.stderr.decode(errors="replace"))
        self.assertIn("navigate()", route.stdout.decode("utf-8"))
        self.assertNotIn(str(self.root), json.dumps(graph))
        manifest_path = output / "knowledge-graph-manifest.json"
        archive_path = output / "knowledge-graph.zip"
        original_archive = archive_path.read_bytes()
        with zipfile.ZipFile(archive_path) as bundle:
            graph_bytes = bundle.read("graph.json")
        for field, value in (
            ("schema_version", 99),
            ("graphify_version", "0.0.0"),
            ("scope", "LLM inference claimed"),
            ("ast_files", []),
            ("document_files", []),
        ):
            changed = dict(manifest, **{field: value})
            common.write_json(manifest_path, changed)
            with zipfile.ZipFile(archive_path, "w") as bundle:
                bundle.writestr("graph.json", graph_bytes)
                bundle.writestr("manifest.json", manifest_path.read_bytes())
            with self.assertRaisesRegex(ValueError, "knowledge graph"):
                graph_release.validate(
                    output / "knowledge-graph.zip", manifest_path, sha, "v0.1.0", manifest["files"]
                )
        common.write_json(manifest_path, manifest)
        archive_path.write_bytes(original_archive)
        self.put("src/app.py", "# dirty\n")
        with self.assertRaisesRegex(ValueError, "clean"):
            graph_release.create(self.root, output, "v0.1.0", sha)


class InstallerTests(unittest.TestCase):
    def test_real_install_is_idempotent_backs_up_and_preserves_other_hooks_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory).resolve()
            original = {
                "permissions": {"deny": ["Bash(rm *)"]},
                "env": {"FIXTURE_LABEL": "\u00c5da"},
                "hooks": {
                    "Stop": [
                        {
                            "hooks": [
                                {"type": "command", "command": "code-review-graph update"},
                                {"type": "command", "command": "echo keep"},
                            ]
                        }
                    ]
                },
            }
            common.write_json(home / ".claude/settings.json", original)
            original_bytes = (
                json.dumps(original, ensure_ascii=False, indent=2)
                .replace("\n", "\r\n")
                .encode("utf-8")
            )
            (home / ".claude/settings.json").write_bytes(original_bytes)
            crg = installer.discover_python()
            first = installer.install(home, crg)
            settings = common.read_json(home / ".claude/settings.json")
            self.assertEqual(settings["permissions"], original["permissions"])
            self.assertEqual(
                settings["hooks"]["Stop"][0]["hooks"], [{"type": "command", "command": "echo keep"}]
            )
            self.assertEqual(
                json.loads(
                    (
                        Path(first["backups"])
                        / installer.backup_name(home / ".claude/settings.json")
                    ).read_text(encoding="utf-8")
                ),
                original,
            )
            self.assertEqual(
                (
                    Path(first["backups"]) / installer.backup_name(home / ".claude/settings.json")
                ).read_bytes(),
                original_bytes,
            )
            before = {
                str(path.relative_to(home)): path.read_bytes()
                for path in home.rglob("*")
                if path.is_file()
            }
            installer.install(home, crg)
            after = {
                str(path.relative_to(home)): path.read_bytes()
                for path in home.rglob("*")
                if path.is_file()
            }
            self.assertEqual(before, after)
            codex = common.read_json(home / ".codex/hooks.json")
            codex_handler = dict(codex["hooks"]["PreToolUse"][-1]["hooks"][0])
            self.assertIn("commandWindows", codex_handler)
            codex_handler.pop("commandWindows")
            self.assertEqual(codex_handler, settings["hooks"]["PreToolUse"][-1]["hooks"][0])
            self.assertFalse((home / ".codex/config.toml").exists())
            self.assertFalse((home / ".codex/hook-trust.json").exists())

    @unittest.skipUnless(
        os.name == "posix", "POSIX modes are checked by Ubuntu CI; Windows ACLs differ"
    )
    def test_private_settings_and_backups_stay_private_with_permissive_umask(self):
        previous_umask = os.umask(0o022)
        try:
            with tempfile.TemporaryDirectory() as directory:
                home = Path(directory).resolve()
                settings = home / ".claude/settings.json"
                original = {"env": {"FIXTURE_TOKEN": "synthetic-only"}}
                common.write_json(settings, original)
                settings.chmod(0o600)
                result = installer.install(home, installer.discover_python())
                self.assertEqual(stat.S_IMODE(settings.stat().st_mode), 0o600)
                backup = Path(result["backups"])
                self.assertEqual(stat.S_IMODE(backup.stat().st_mode), 0o700)
                for path in backup.iterdir():
                    self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
                self.assertEqual(
                    common.read_json(backup / installer.backup_name(settings)), original
                )
                self.assertEqual(stat.S_IMODE((home / ".codex/hooks.json").stat().st_mode), 0o600)
                self.assertEqual(common.read_json(settings)["env"], original["env"])
        finally:
            os.umask(previous_umask)

    def test_installed_command_executes_through_native_shell_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix="graph home ") as directory:
            home = Path(directory).resolve()
            installer.install(home, installer.discover_python())
            handler = common.read_json(home / ".codex/hooks.json")["hooks"]["SessionStart"][0][
                "hooks"
            ][0]
            if os.name == "nt":
                argv = [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    handler["commandWindows"],
                ]
            else:
                argv = ["sh", "-c", handler["command"]]
            result = subprocess.run(
                argv,
                input=b'{"hook_event_name":"SessionStart"}',
                capture_output=True,
                timeout=20,
                cwd=home,
            )
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            self.assertIn(
                "Graph-first", json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
            )

    def test_malformed_settings_fail_before_runtime_or_instruction_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            (home / ".claude").mkdir()
            path = home / ".claude/settings.json"
            for malformed in ("{broken", '{"hooks": []}', "[]"):
                path.write_text(malformed, encoding="utf-8")
                with self.assertRaises(ValueError):
                    installer.install(home, installer.discover_python())
                self.assertEqual(path.read_text(encoding="utf-8"), malformed)
                self.assertFalse((home / ".local/share/agent-graph-first").exists())


class UIReferenceTests(RepoCase):
    def catalog(self):
        self.put("src/view.py", "# UI\n")

        def chunk(kind, body):
            return (
                struct.pack(">I", len(body))
                + kind
                + body
                + struct.pack(">I", zlib.crc32(kind + body))
            )

        image = (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff"))
            + chunk(b"IEND", b"")
        )
        path = self.root / "docs/ui-reference/main.png"
        path.parent.mkdir(parents=True)
        path.write_bytes(image)
        data = {
            "schema_version": 1,
            "mode": "ui",
            "source_patterns": ["src/**"],
            "required_states": ["phone/main"],
            "source_hashes": ui_reference.source_hashes(self.root, ["src/**"]),
            "entries": [
                {
                    "state": "phone/main",
                    "image": "main.png",
                    "sha256": hashlib.sha256(image).hexdigest(),
                    "dimensions": [1, 1],
                    "reviewer": "Synthetic fixture reviewer",
                    "approved_at": "2026-10-17T00:00:00Z",
                    "evidence": "Fixture, not a product approval",
                    "configuration": "1x1 fixture",
                }
            ],
        }
        common.write_json(self.root / "docs/ui-reference/catalog.json", data)
        return data

    def test_latest_reference_rejects_source_and_image_changes(self):
        data = self.catalog()
        ui_reference.validate(self.root)
        self.put("src/view.py", "# changed UI\n")
        with self.assertRaisesRegex(ValueError, "stale"):
            ui_reference.validate(self.root)
        data["source_hashes"] = ui_reference.source_hashes(self.root, ["src/**"])
        common.write_json(self.root / "docs/ui-reference/catalog.json", data)
        (self.root / "docs/ui-reference/main.png").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "image changed"):
            ui_reference.validate(self.root)

    def test_missing_states_approval_and_unsafe_images_are_rejected(self):
        data = self.catalog()
        for field, value in (
            ("reviewer", ""),
            ("image", "../outside.png"),
            ("approved_at", "yesterday"),
        ):
            candidate = copy.deepcopy(data)
            candidate["entries"][0][field] = value
            common.write_json(self.root / "docs/ui-reference/catalog.json", candidate)
            with self.assertRaises((ValueError, OSError)):
                ui_reference.validate(self.root)
        data["required_states"].append("monitor/main/r90")
        common.write_json(self.root / "docs/ui-reference/catalog.json", data)
        with self.assertRaisesRegex(ValueError, "states"):
            ui_reference.validate(self.root)

    def test_no_ui_requires_explicit_empty_scope_and_reason(self):
        catalog = self.root / "docs/ui-reference/catalog.json"
        common.write_json(
            catalog,
            {
                "schema_version": 1,
                "mode": "no-ui",
                "reason": "CLI only",
                "entries": [],
                "source_patterns": [],
            },
        )
        ui_reference.validate(self.root)
        common.write_json(catalog, {"schema_version": 1, "mode": "no-ui", "entries": []})
        with self.assertRaises(ValueError):
            ui_reference.validate(self.root)
