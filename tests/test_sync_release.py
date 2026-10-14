"""Common suite source integrity and reference archive independence checks.

Author: yinjie.
"""

import importlib.util
import json
from pathlib import Path
import shutil
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sync_release", ROOT / "scripts/sync_release.py")
sync_release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_release)
RELEASE = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))


class ReleaseSyncTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / "output/sync-tests"
        scratch.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        shutil.copytree(ROOT / sync_release.SKILL_PATH, self.root / sync_release.SKILL_PATH)
        shutil.copyfile(ROOT / "release-manifest.json", self.root / "release-manifest.json")
        patch = mock.patch.object(sync_release, "ROOT", self.root)
        patch.start()
        self.addCleanup(patch.stop)
        # Fixtures represent a refreshed checkout even while the live source is
        # being synchronized; tests never rewrite the repository's metadata.
        self.initial_release = sync_release.sync()

    def snapshot(self):
        return {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.root.rglob("*") if p.is_file()}

    def test_entries_digest_matches_existing_v1_encoding(self):
        # Known vector encoded independently using big-endian >QQ lengths
        # followed by both byte sequences; includes UTF-8 and binary content.
        entries = {"é.txt": b"data", "b.txt": b"\0\xff", "a.txt": b"x"}
        self.assertEqual("fc215518cf3ad6471c239814072552a587ed343a14e916f33d37cfc57b2c7c88",
                         sync_release.entries_digest(entries))

    def test_source_names_reject_traversal_and_windows_special_paths(self):
        for name in ("../outside", "a/../outside", "C:/file", "a\\b", "file:stream",
                     "NUL.txt", "file.", "a//b", "/file", "aux?/test.txt", 'a"b', "file*"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Unsafe"):
                sync_release.validate_name(name)

    def test_reparse_point_is_rejected_without_is_junction_api(self):
        with mock.patch.object(Path, "lstat", return_value=SimpleNamespace(st_file_attributes=0x400)), \
                mock.patch.object(Path, "is_symlink", return_value=False):
            with self.assertRaisesRegex(ValueError, "Linked output path"):
                sync_release.safe_target(Path("output/reparse-check"))

    def test_source_reparse_point_fails_before_any_write(self):
        path = self.root / sync_release.SKILL_PATH / "references"
        before = self.snapshot()
        original = Path.lstat
        def linked(target, *args, **kwargs):
            if target == path:
                return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
            return original(target, *args, **kwargs)
        with mock.patch.object(Path, "lstat", linked):
            with self.assertRaisesRegex(ValueError, "Linked output path"):
                sync_release.sync()
        self.assertEqual(before, self.snapshot())

    def test_sync_is_repeatable_and_check_is_read_only(self):
        result = sync_release.sync()
        self.assertEqual(self.initial_release["commonFiles"], result["commonFiles"])
        self.assertEqual("plugins/common/aholo-lux3d", result["skillPath"])
        before = self.snapshot()
        sync_release.sync(check=True)
        self.assertEqual(before, self.snapshot())
        sync_release.sync()
        self.assertEqual(before, self.snapshot())

    def test_check_detects_unrecorded_source_changes_and_missing_files(self):
        sync_release.sync()
        path = self.root / sync_release.SKILL_PATH / "scripts/commerce.py"
        path.write_text("changed runtime", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Source integrity drift"):
            sync_release.sync(check=True)
        sync_release.sync()
        sync_release.sync(check=True)
        path.unlink()
        with self.assertRaisesRegex(ValueError, "Missing Common Skill resource"):
            sync_release.sync()

    def test_extra_skill_and_host_identity_changes_are_rejected(self):
        skill = self.root / sync_release.SKILL_PATH
        extra = skill / "nested/SKILL.md"
        extra.parent.mkdir()
        extra.write_text("unexpected")
        with self.assertRaisesRegex(ValueError, "exactly one root Skill"):
            sync_release.sync()
        extra.unlink()
        adapter = json.loads((skill / "adapter.json").read_text())
        adapter["source"] = 1
        (skill / "adapter.json").write_text(json.dumps(adapter))
        with self.assertRaisesRegex(ValueError, "automatic-host"):
            sync_release.sync()

    def test_source_refresh_preserves_suite_reference_archive_and_sidecars(self):
        paths = [self.root / RELEASE["upstreamArtifact"][key]
                 for key in ("path", "checksumPath", "releaseRecordPath")]
        for index, path in enumerate(paths):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(f"suite reference fixture {index}".encode())
        before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths}
        body = self.root / sync_release.SKILL_PATH / "body.md"
        body.write_bytes(body.read_bytes() + b"\nMaintained source change.\n")
        sync_release.sync()
        sync_release.sync(check=True)
        self.assertEqual(before, {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths})
        manifest = json.loads((self.root / "release-manifest.json").read_text())
        self.assertEqual(RELEASE["upstreamArtifact"], manifest["upstreamArtifact"])
        self.assertIn(b"Maintained source change", body.read_bytes())
        self.assertNotEqual(RELEASE["source"]["sha256"], manifest["source"]["sha256"])

    def test_source_checks_need_neither_archive_nor_sidecars(self):
        self.assertFalse((self.root / RELEASE["upstreamArtifact"]["path"]).exists())
        sync_release.sync()
        sync_release.sync(check=True)
        self.assertFalse((self.root / "lux3d-plugin").exists())

    def test_suite_records_routes_and_refreshes_connector_integrity(self):
        result = sync_release.sync()
        skill = self.root / sync_release.SKILL_PATH
        build = json.loads((skill / "build-info.json").read_text())
        manifest = json.loads((self.root / "release-manifest.json").read_text())
        self.assertEqual("suite", build["mode"])
        self.assertEqual("suite", manifest["skill"]["packageMode"])
        self.assertEqual(["openapi", "mcp"], manifest["skill"]["executionModes"])
        installation = manifest["installation"]
        self.assertEqual(["local-skills"], installation["requires"])
        self.assertIn("python>=3.10", installation["helperRequires"])
        self.assertIn("python>=3.10", installation["executionRequirements"]["openapi"])
        self.assertEqual(["mcp-remote", "tool-discovery", "credential-injection"],
                         installation["executionRequirements"]["mcp"])
        self.assertEqual("github-skill-source-mcp-references", build["connectorDigestSource"])
        original = build["connectorDigest"]
        workflow = skill / "references/mcp/workflow.md"
        workflow.write_bytes(workflow.read_bytes() + b"\nMaintained connector guidance.\n")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "Source integrity drift"):
            sync_release.sync(check=True)
        self.assertEqual(before, self.snapshot())
        refreshed = sync_release.sync()
        self.assertNotEqual(result["sourceSha256"], refreshed["sourceSha256"])
        build = json.loads((skill / "build-info.json").read_text())
        self.assertNotEqual(original, build["connectorDigest"])
        files = sync_release.tree_files(skill)
        self.assertEqual(sync_release.entries_digest({n: value for n, value in files.items()
                                                      if n.startswith("references/mcp/")}),
                         build["connectorDigest"])
        sync_release.sync(check=True)

    def test_suite_requires_both_complete_workflows_before_refresh(self):
        skill = self.root / sync_release.SKILL_PATH
        for name in sync_release.SUITE_RESOURCES:
            path = skill / name
            payload = path.read_bytes()
            path.unlink()
            before = self.snapshot()
            with self.subTest(resource=name), self.assertRaisesRegex(ValueError, "Missing Common suite resource"):
                sync_release.sync()
            self.assertEqual(before, self.snapshot())
            path.write_bytes(payload)

    def test_suite_rejects_wrong_slot_and_cross_route_requirements(self):
        path = self.root / sync_release.SKILL_PATH / "release-contract.json"
        original = path.read_bytes()
        for issue in ("slot", "region", "mcp-python"):
            contract = json.loads(original)
            if issue == "slot":
                contract["discovery"]["suite"]["slot"] = "aholo-lux3d-mcp"
            elif issue == "region":
                contract["regions"]["suite"] = ["cn"]
            else:
                contract["capabilities"]["suite"]["selectedModeRequirements"]["mcp"].append("python")
            path.write_bytes(sync_release.json_bytes(contract))
            before = self.snapshot()
            with self.subTest(issue=issue), self.assertRaisesRegex(ValueError, "Invalid Common suite"):
                sync_release.sync()
            self.assertEqual(before, self.snapshot())
        path.write_bytes(original)

    def test_suite_rejects_wrong_region_credentials_or_automatic_fallback(self):
        path = self.root / sync_release.SKILL_PATH / "references/mcp/connection.json"
        original = path.read_bytes()
        for issue in ("region", "credentials", "fallback", "create-retry", "source-override", "native-descriptor"):
            connection = json.loads(original)
            if issue == "region":
                connection["regions"]["international"]["endpoint"] = connection["regions"]["cn"]["endpoint"]
            elif issue == "credentials":
                connection["regions"]["international"]["environmentVariable"] = "LUX3D_CN_API_KEY"
            elif issue == "fallback":
                connection["policy"]["crossRegionFallback"] = True
            elif issue == "create-retry":
                connection["policy"]["automaticCreateRetry"] = True
            elif issue == "source-override":
                connection["identity"]["sourceOverrideAllowed"] = True
            else:
                connection["descriptorIsHostNative"] = True
            path.write_bytes(sync_release.json_bytes(connection))
            before = self.snapshot()
            with self.subTest(issue=issue), self.assertRaisesRegex(ValueError, "Invalid Common suite MCP"):
                sync_release.sync()
            self.assertEqual(before, self.snapshot())
        path.write_bytes(original)

    def test_suite_rejects_different_host_registry_and_unverified_schema_authority(self):
        skill = self.root / sync_release.SKILL_PATH
        path = skill / "references/mcp/host-identity.json"
        original = path.read_bytes()
        registry = json.loads(original)
        registry["knownHosts"]["workbuddy"]["source"] = 100
        path.write_bytes(sync_release.json_bytes(registry))
        with self.assertRaisesRegex(ValueError, "share the automatic host registry"):
            sync_release.sync()
        path.write_bytes(original)
        path = skill / "references/mcp/tool-map.json"
        tool_map = json.loads(path.read_text())
        tool_map["inputSchemaAuthority"] = "bundled-reference-only"
        path.write_bytes(sync_release.json_bytes(tool_map))
        with self.assertRaisesRegex(ValueError, "Invalid Common suite MCP tool reference"):
            sync_release.sync()

    def test_suite_mode_is_required_before_any_metadata_write(self):
        path = self.root / sync_release.SKILL_PATH / "build-info.json"
        build = json.loads(path.read_text())
        build["mode"] = "skill"
        path.write_bytes(sync_release.json_bytes(build))
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "automatic-host Common suite"):
            sync_release.sync()
        self.assertEqual(before, self.snapshot())

    def test_check_rejects_host_specific_distribution(self):
        obsolete = self.root / "plugins/codex"
        obsolete.mkdir()
        with self.assertRaisesRegex(ValueError, "Host-specific distribution"):
            sync_release.sync(check=True)
        self.assertTrue(obsolete.is_dir(), "Read-only checks must preserve obsolete paths")


if __name__ == "__main__":
    unittest.main()
