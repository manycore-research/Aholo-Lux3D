"""Maintained source integrity and historical archive independence checks.

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
        self.assertEqual(RELEASE["source"]["fileCount"], result["commonFiles"])
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

    def test_source_refresh_preserves_historical_archive_and_sidecars(self):
        paths = [self.root / RELEASE["archive"][key]
                 for key in ("path", "checksumPath", "releaseRecordPath")]
        for index, path in enumerate(paths):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(f"historical fixture {index}".encode())
        before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths}
        body = self.root / sync_release.SKILL_PATH / "body.md"
        body.write_bytes(body.read_bytes() + b"\nMaintained source change.\n")
        sync_release.sync()
        sync_release.sync(check=True)
        self.assertEqual(before, {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths})
        manifest = json.loads((self.root / "release-manifest.json").read_text())
        self.assertEqual(RELEASE["archive"], manifest["archive"])
        self.assertIn(b"Maintained source change", body.read_bytes())
        self.assertNotEqual(RELEASE["source"]["sha256"], manifest["source"]["sha256"])

    def test_source_checks_need_neither_archive_nor_sidecars(self):
        self.assertFalse((self.root / RELEASE["archive"]["path"]).exists())
        sync_release.sync()
        sync_release.sync(check=True)
        self.assertFalse((self.root / "lux3d-plugin").exists())

    def test_archive_import_is_explicitly_rejected_without_changes(self):
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "Archive import is no longer supported"):
            sync_release.sync(self.root / "historical.zip")
        self.assertEqual(before, self.snapshot())

    def test_check_rejects_obsolete_codex_distribution(self):
        obsolete = self.root / "plugins/codex"
        obsolete.mkdir()
        with self.assertRaisesRegex(ValueError, "Obsolete Codex distribution"):
            sync_release.sync(check=True)
        self.assertTrue(obsolete.is_dir(), "Read-only checks must preserve obsolete paths")


if __name__ == "__main__":
    unittest.main()
