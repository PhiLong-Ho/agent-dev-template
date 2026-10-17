import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bootstrap
import check_docs
import evidence
import project
import quality
import release
import review_gate
import run_tests


class ProjectTests(unittest.TestCase):
    def test_rejects_invalid_command_and_identity_configurations(self):
        good = project.load()
        for key, value in [
            ("name", "../escape"),
            ("repository", "wrong"),
            ("version", "../1"),
            ("commands", []),
            ("test_results", ["../result.json"]),
        ]:
            bad = copy.deepcopy(good)
            bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                project.validate(bad)
        bad = copy.deepcopy(good)
        bad["commands"][0]["argv"] = "shell command"
        with self.assertRaises(ValueError):
            project.validate(bad)

    def test_argument_arrays_preserve_literal_shell_metacharacters(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            command = {
                "name": "literal",
                "argv": ["{python}", "-c", "import sys; print(sys.argv[1])", "$(secret) & literal"],
            }
            result = project.execute(root, [command], root / "logs")
            self.assertEqual(result[0]["exit_code"], 0)
            self.assertIn(b"$(secret) & literal", (root / "logs/literal.log").read_bytes())

    def test_nonzero_and_missing_commands_retain_failure_logs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            commands = [
                {"name": "bad", "argv": ["{python}", "-c", "raise SystemExit(4)"]},
                {"name": "missing", "argv": [str(root / "no-executable")]},
            ]
            results = project.execute(root, commands, root / "logs")
            self.assertEqual([4, 127], [row["exit_code"] for row in results])
            self.assertTrue((root / "logs/missing.log").exists())


class BootstrapTests(unittest.TestCase):
    def test_initialization_changes_identity_and_removes_inherited_approvals_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            project.write_json(root / "project.json", project.load())
            project.write_json(root / "reviews/approvals.json", {"old": True})
            (root / "source.txt").write_bytes(b"keep\r\n")
            bootstrap.initialize(root, "new-project", "owner/new-project")
            self.assertEqual(project.load(root)["repository"], "owner/new-project")
            bootstrap.check_repository(root, "owner/new-project")
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                bootstrap.check_repository(root, "template/old-project")
            empty = project.read_json(root / "reviews/approvals.json")
            self.assertEqual(empty["reviews"], [])
            with self.assertRaises(ValueError):
                review_gate.validate(empty, "candidate")
            self.assertEqual((root / "source.txt").read_bytes(), b"keep\r\n")

    def test_invalid_initialization_preserves_existing_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            project.write_json(root / "project.json", project.load())
            before = (root / "project.json").read_bytes()
            with self.assertRaises(ValueError):
                bootstrap.initialize(root, "../bad", "owner/repo")
            self.assertEqual(before, (root / "project.json").read_bytes())

    def test_remote_protection_errors_and_incomplete_response_fail(self):
        for result in [
            subprocess.CompletedProcess([], 1, "", "permission denied"),
            subprocess.CompletedProcess([], 0, "{}", ""),
        ]:
            with (
                self.subTest(result=result),
                mock.patch.object(
                    bootstrap.subprocess,
                    "run",
                    side_effect=[
                        subprocess.CompletedProcess(
                            [], 0, json.dumps({"nameWithOwner": project.load()["repository"]}), ""
                        ),
                        subprocess.CompletedProcess([], 1, "HTTP/2.0 404 Not Found\n\n{}", ""),
                        result,
                    ],
                ),
                self.assertRaises(ValueError),
            ):
                bootstrap.protect(project.ROOT)
        with mock.patch.object(
            bootstrap.subprocess,
            "run",
            return_value=subprocess.CompletedProcess([], 0, '{"nameWithOwner":"other/repo"}', ""),
        ) as call:
            with self.assertRaisesRegex(ValueError, "does not match"):
                bootstrap.protect(project.ROOT)
            self.assertEqual(call.call_count, 1)

    def test_protection_targets_configured_repo_and_requires_strict_response(self):
        payload = project.read_json(project.ROOT / "config/github/main-protection.json")
        state = {
            "enforce_admins": {"enabled": True},
            "required_status_checks": payload["required_status_checks"],
            "required_pull_request_reviews": payload["required_pull_request_reviews"],
            "allow_force_pushes": {"enabled": False},
            "allow_deletions": {"enabled": False},
            "required_conversation_resolution": {"enabled": True},
        }
        with mock.patch.object(
            bootstrap.subprocess,
            "run",
            side_effect=[
                subprocess.CompletedProcess(
                    [], 0, json.dumps({"nameWithOwner": project.load()["repository"]}), ""
                ),
                subprocess.CompletedProcess([], 1, "HTTP/2.0 404 Not Found\n\n{}", ""),
                subprocess.CompletedProcess([], 0, json.dumps(state), ""),
            ],
        ) as call:
            bootstrap.protect(project.ROOT)
        self.assertIn(
            f"repos/{project.load()['repository']}/branches/main/protection", call.call_args.args[0]
        )
        self.assertEqual(json.loads(call.call_args.kwargs["input"]), payload)

    def test_existing_or_uninspectable_protection_is_never_overwritten(self):
        for result in [
            subprocess.CompletedProcess([], 0, '{"stronger":"rules"}', ""),
            subprocess.CompletedProcess([], 1, "HTTP/2.0 403 Forbidden\n\n{}", "denied"),
        ]:
            with (
                self.subTest(result=result),
                mock.patch.object(
                    bootstrap.subprocess,
                    "run",
                    side_effect=[
                        subprocess.CompletedProcess(
                            [], 0, json.dumps({"nameWithOwner": project.load()["repository"]}), ""
                        ),
                        result,
                    ],
                ) as calls,
            ):
                with self.assertRaises(ValueError):
                    bootstrap.protect(project.ROOT)
                self.assertEqual(calls.call_count, 2)
                self.assertFalse(any("PUT" in call.args[0] for call in calls.call_args_list))


class OutcomeTests(unittest.TestCase):
    def test_quality_retains_nonzero_command_and_refuses_missing_results(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            config = project.load()
            config["commands"] = [
                {
                    "name": "bad",
                    "argv": ["{python}", "-c", "print('raw failure'); raise SystemExit(9)"],
                }
            ]
            project.write_json(root / "project.json", config)
            project.write_json(root / "docs/requirements.json", {})
            (root / ".gitignore").write_text("artifacts/\n", encoding="utf-8")
            with (
                mock.patch.object(quality.check_requirements, "validate", return_value=[]),
                mock.patch.object(quality.coverage, "check"),
                mock.patch.object(quality.check_docs, "validate", return_value=[]),
            ):
                result = quality.run(root, root / "artifacts/failed")
            self.assertFalse(result["passed"])
            self.assertEqual(result["commands"][0]["exit_code"], 9)
            self.assertIn(b"raw failure", (root / "artifacts/failed/bad.log").read_bytes())
            self.assertTrue((root / "artifacts/failed/host-results.json").exists())

    def test_missing_empty_duplicate_bad_status_and_source_results_fail(self):
        valid = {
            "schema_version": 1,
            "source_commit": "abc",
            "cases": [{"id": "example", "status": "passed"}],
        }
        for replacement in [
            [],
            [{"id": "a", "status": "invented"}],
            valid["cases"] * 2,
            [{"id": "", "status": "passed"}],
        ]:
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                quality.count_results([{**valid, "cases": replacement}], "abc")
        with self.assertRaises(ValueError):
            quality.count_results([valid], "different")

    def test_skips_failures_and_errors_are_counted_separately(self):
        statuses = [
            "passed",
            "failed",
            "error",
            "skipped",
            "expected_failure",
            "unexpected_success",
        ]
        data = {
            "schema_version": 1,
            "source_commit": "abc",
            "cases": [{"id": value, "status": value} for value in statuses],
        }
        self.assertEqual(quality.count_results([data], "abc"), dict.fromkeys(statuses, 1))

    def test_recording_runner_preserves_actual_failure_and_skip(self):
        class Fixture(unittest.TestCase):
            def test_pass(self):
                self.assertTrue(True)

            def test_fail(self):
                self.fail("intentional fixture")

            @unittest.skip("fixture")
            def test_skip(self):
                pass

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "outcomes.json"
            code = run_tests.run_tests(
                unittest.defaultTestLoader.loadTestsFromTestCase(Fixture), path, "abc"
            )
            self.assertEqual(code, 1)
            self.assertEqual(
                sorted(row["status"] for row in project.read_json(path)["cases"]),
                ["failed", "passed", "skipped"],
            )


class DocumentationTests(unittest.TestCase):
    def test_filesystem_path_aliases_report_link_errors_without_crashing(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            path = root / "README.md"
            path.write_text("[bad](missing.md)\n[escape](../outside.md)\n", encoding="utf-8")
            alias = root.parent / (root.name + "-short-alias")
            original = Path.resolve

            def resolve(candidate, *args, **kwargs):
                if candidate == alias:
                    return root
                if candidate == alias / "README.md":
                    return path
                return original(candidate, *args, **kwargs)

            with mock.patch.object(Path, "resolve", autospec=True, side_effect=resolve):
                errors = check_docs.check_links(alias, [alias / "README.md"])
            self.assertEqual(len(errors), 2)
            self.assertTrue(all("missing/outside local link" in error for error in errors))

    def test_broken_or_outside_links_fail_but_fenced_examples_are_ignored(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / "README.md"
            path.write_text(
                "[bad](missing.md)\n[escape](../outside.md)\n```sh\n[example](not-real.md)\n```\n",
                encoding="utf-8",
            )
            self.assertEqual(len(check_docs.check_links(root, [path])), 2)

    def test_repository_docs_and_spec_sections_are_valid(self):
        self.assertEqual(check_docs.validate(project.ROOT), [])


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        config = project.load()
        config.update(name="fixture", repository="owner/repo", version="0.1.0")
        project.write_json(self.root / "project.json", config)
        (self.root / ".gitignore").write_text("artifacts/\n", encoding="utf-8")
        (self.root / "CHANGELOG.md").write_text(
            "# Changelog\n\n## [0.1.0] - fixture\n\n- Fixture release\n", encoding="utf-8"
        )
        project.write_json(
            self.root / "docs/requirements.json",
            {
                "requirements": [
                    {"id": "WF-FIXTURE-001", "coverage": "partial", "gap": "Fixture only"}
                ]
            },
        )
        project.write_json(self.root / "docs/coverage-snapshot.json", {"fixture": True})
        self.git("add", ".")
        record = {
            "schema_version": 1,
            "candidate_sha256": review_gate.candidate(self.root),
            "reviews": [
                {
                    "agent_id": identity,
                    "fresh_agent": True,
                    "verdict": "approve",
                    "reviewed_at": "2026-01-01T00:00:00Z",
                    "scope": "Synthetic fixture",
                    "summary": "Fixture only",
                }
                for identity in ["fixture-a", "fixture-b"]
            ],
        }
        project.write_json(self.root / review_gate.RECORD, record)
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        self.git("tag", "v0.1.0")
        self.output = self.root / "artifacts/release"

    def git(self, *args):
        return project.git(self.root, *args)

    def package(self, artifact="example-0.1.0.zip"):
        def host(root, folder):
            folder.mkdir(parents=True)
            state = project.source_state(root)
            project.write_json(folder / "source.json", state)
            project.write_json(
                folder / "tests.json",
                {
                    "schema_version": 1,
                    "source_commit": state["commit"],
                    "cases": [{"id": "fixture", "status": "passed"}],
                },
            )
            result = {
                "passed": True,
                "source": state,
                "source_unchanged": True,
                "tests": quality.test_counts(folder, ["tests.json"], state["commit"]),
                "validation": [{"name": "fixture", "exit_code": 0}],
                "commands": [{"name": "fixture", "exit_code": 0}],
                "scope": "Synthetic fixture only",
            }
            project.write_json(folder / "host-results.json", result)
            return result

        def build(root, commands, folder, **values):
            output = Path(values["output"])
            output.mkdir(parents=True)
            (output / artifact).write_bytes(b"fixture artifact")
            return [{"name": "fixture", "exit_code": 0}]

        with (
            mock.patch.object(release.quality, "run", side_effect=host),
            mock.patch.object(release.project, "execute", side_effect=build),
        ):
            release.build(
                self.root, self.output, "v0.1.0", "https://github.com/owner/repo/actions/runs/123"
            )

    def reseal(self):
        metadata = project.read_json(self.output / "package.json")
        for name in metadata["files"]:
            metadata["files"][name] = evidence.digest_file(self.output / name)
        project.write_json(self.output / "package.json", metadata)
        (self.output / "SHA256SUMS.txt").write_text(
            "".join(
                f"{evidence.digest_file(self.output / name)}  {name}\n"
                for name in sorted(set(metadata["files"]) | {"package.json"})
            ),
            encoding="utf-8",
        )

    def rewrite_archive(self, mutate):
        archive = self.output / "release-evidence.zip"
        with zipfile.ZipFile(archive) as bundle:
            files = {item.filename: bundle.read(item) for item in bundle.infolist()}
        manifest = json.loads(files.pop("manifest.json"))
        mutate(files, manifest)
        for record in manifest["files"]:
            data = files["data/" + record["path"]]
            record.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        with zipfile.ZipFile(archive, "w") as bundle:
            for name, data in files.items():
                bundle.writestr(name, data)
            bundle.writestr("manifest.json", json.dumps(manifest))
        descriptor = project.read_json(self.output / "release-evidence.json")
        descriptor.update(
            archive_sha256=evidence.digest_file(archive),
            archive_bytes=archive.stat().st_size,
            context=manifest["context"],
            raw_bytes=sum(record["bytes"] for record in manifest["files"]),
        )
        project.write_json(self.output / "release-evidence.json", descriptor)
        self.reseal()

    def test_resealed_raw_test_or_source_context_mismatch_is_rejected(self):
        self.package()

        def change_test(files, manifest):
            result = json.loads(files["data/tests.json"])
            result["cases"][0]["status"] = "failed"
            files["data/tests.json"] = json.dumps(result).encode("utf-8")

        self.rewrite_archive(change_test)
        with self.assertRaisesRegex(ValueError, "counts/rate"):
            release.validate(self.root, self.output)

    def test_resealed_wrong_archive_commit_is_rejected(self):
        self.package()

        def change_context(files, manifest):
            manifest["context"]["source_commit"] = "wrong"

        self.rewrite_archive(change_context)
        with self.assertRaisesRegex(ValueError, "Archive source mismatch"):
            release.validate(self.root, self.output)

    def test_valid_package_binds_reports_counts_sources_and_assets(self):
        self.package()
        release.validate(self.root, self.output)
        report = project.read_json(self.output / "release-report.json")
        self.assertEqual(report["tests"]["passed"], 1)
        self.assertEqual(report["pass_rate"], 1)
        self.assertEqual(report["gaps"][0]["gap"], "Fixture only")
        with mock.patch.object(
            release.subprocess,
            "run",
            side_effect=[
                subprocess.CompletedProcess([], 0, "[[]]", ""),
                subprocess.CompletedProcess([], 0),
                subprocess.CompletedProcess([], 0),
            ],
        ) as calls:
            with mock.patch.object(
                release, "validate", return_value=project.read_json(self.output / "package.json")
            ):
                release.publish(self.root, self.output)
        self.assertIn("--draft", calls.call_args_list[1].args[0])
        self.assertIn("--draft=false", calls.call_args_list[2].args[0])
        self.assertTrue(
            any("release-evidence.zip" in arg for arg in calls.call_args_list[1].args[0])
        )

    def test_hidden_nonzip_artifact_survives_exact_export_and_import_validation(self):
        config = project.load(self.root)
        config["release"]["artifacts"] = ["*.whl"]
        project.write_json(self.root / "project.json", config)
        self.git("add", "project.json")
        record = project.read_json(self.root / review_gate.RECORD)
        record["candidate_sha256"] = review_gate.candidate(self.root)
        project.write_json(self.root / review_gate.RECORD, record)
        self.git("add", review_gate.RECORD)
        self.git("commit", "-qm", "configured fixture artifact")
        self.git("tag", "-f", "v0.1.0")
        self.package(".example-0.1.0.whl")
        destination = self.root / "artifacts/transferred"
        release.export_package(self.root, self.output, destination)
        metadata = release.validate(self.root, destination)
        self.assertEqual(
            {path.name for path in destination.iterdir()},
            set(metadata["files"]) | {"package.json", "SHA256SUMS.txt"},
        )
        self.assertEqual((destination / ".example-0.1.0.whl").read_bytes(), b"fixture artifact")
        self.assertFalse(any(path.is_dir() for path in destination.iterdir()))

    def test_missing_or_corrupt_evidence_refuses_before_remote_call(self):
        self.package()
        archive = self.output / "release-evidence.zip"
        original = archive.read_bytes()
        for failure in ["corrupt", "missing"]:
            if failure == "corrupt":
                archive.write_bytes(original + b"changed")
            else:
                archive.unlink()
            with (
                self.subTest(failure=failure),
                mock.patch.object(release.subprocess, "run") as remote,
            ):
                with mock.patch.object(
                    release,
                    "context",
                    return_value=(
                        project.load(self.root),
                        project.read_json(self.output / "package.json")["source"],
                    ),
                ):
                    with self.assertRaises((ValueError, OSError)):
                        release.publish(self.root, self.output)
                remote.assert_not_called()

    def test_resealed_report_mismatch_is_rejected(self):
        self.package()
        report = project.read_json(self.output / "release-report.json")
        report["tests"]["passed"] = 999
        project.write_json(self.output / "release-report.json", report)
        (self.output / "release-report.md").write_text(
            release.render_report(report), encoding="utf-8"
        )
        self.reseal()
        with self.assertRaisesRegex(ValueError, "Archived report mismatch"):
            release.validate(self.root, self.output)

    def test_wrong_tag_dirty_source_and_stale_reviews_refuse_build(self):
        for tag in ["v9.0.0", "../../bad"]:
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                release.build(
                    self.root, self.output, tag, "https://github.com/owner/repo/actions/runs/123"
                )
        (self.root / "new-source.py").write_text("changed\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "clean"):
            self.package()
        self.git("add", ".")
        self.git("commit", "-qm", "unreviewed")
        self.git("tag", "-f", "v0.1.0")
        with self.assertRaisesRegex(ValueError, "stale"):
            self.package()

    def test_existing_published_or_draft_release_is_never_overwritten(self):
        self.package()
        metadata = release.validate(self.root, self.output)
        for draft in [False, True]:
            with (
                self.subTest(draft=draft),
                mock.patch.object(release, "validate", return_value=metadata),
                mock.patch.object(
                    release.subprocess,
                    "run",
                    return_value=subprocess.CompletedProcess(
                        [], 0, json.dumps([[{"tag_name": "v0.1.0", "draft": draft}]]), ""
                    ),
                ) as calls,
            ):
                with self.assertRaisesRegex(ValueError, "already exists"):
                    release.publish(self.root, self.output)
                self.assertEqual(calls.call_count, 1)

    def test_failed_host_check_retains_raw_attempt_without_release_package(self):
        def failed(root, folder):
            project.write_json(
                folder / "host-results.json", {"passed": False, "scope": "Failure fixture"}
            )
            return {"passed": False}

        with (
            mock.patch.object(release.quality, "run", side_effect=failed),
            self.assertRaisesRegex(ValueError, "host checks failed"),
        ):
            release.build(
                self.root, self.output, "v0.1.0", "https://github.com/owner/repo/actions/runs/123"
            )
        self.assertFalse((self.output / "package.json").exists())
        self.assertFalse(project.read_json(self.output / "raw/host-results.json")["passed"])

    def test_missing_empty_or_duplicate_changelog_notes_are_rejected(self):
        path = self.root / "CHANGELOG.md"
        for text in [
            "# Changelog\n",
            "# Changelog\n\n## [0.1.0] - date",
            "# Changelog\n\n## [0.1.0] - date\n\n",
            "# Changelog\n\n## [0.1.0]\n- One\n\n## [0.1.0]\n- Two\n",
        ]:
            path.write_text(text, encoding="utf-8")
            with self.subTest(text=text), self.assertRaises(ValueError):
                release.notes(self.root, "0.1.0")
