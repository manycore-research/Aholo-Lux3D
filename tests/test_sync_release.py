"""Release integrity and extraction boundaries; no network or installation."""

import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
import zipfile


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sync_release", ROOT / "scripts/sync_release.py")
sync_release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_release)
COMMON = ROOT / "lux3d-plugin/common/lux3d-plugin-1.1.0-common-skill.zip"


class ReleaseSyncTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / "output/sync-tests"
        scratch.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()

    def archive(self, names):
        path = self.root / "test.zip"
        with zipfile.ZipFile(path, "w") as archive:
            for name in names:
                # Preserve raw ZIP spelling even on Windows, where ZipInfo's
                # constructor otherwise normalizes backslashes to slashes.
                entry = name if isinstance(name, zipfile.ZipInfo) else zipfile.ZipInfo()
                if isinstance(name, str):
                    entry.filename = entry.orig_filename = name
                archive.writestr(entry, b"test")
        path.with_suffix(".zip.sha256").write_text(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  test.zip\n", encoding="utf-8")
        return path

    def initialize(self):
        patch = mock.patch.object(sync_release, "ROOT", self.root)
        patch.start()
        self.addCleanup(patch.stop)
        return sync_release.sync(COMMON)

    def test_archive_rejects_checksum_mismatch(self):
        archive = self.archive(["aholo-lux3d/SKILL.md"])
        archive.with_suffix(".zip.sha256").write_text("0" * 64 + "  test.zip\n")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            sync_release.read_archive(archive)

    def test_archive_rejects_traversal_and_windows_special_paths(self):
        for name in ("../outside", "aholo-lux3d/../outside", "aholo-lux3d/C:/file",
                     "aholo-lux3d/a\\b", "aholo-lux3d/file:stream", "aholo-lux3d/NUL.txt",
                     "aholo-lux3d/file.", "aholo-lux3d/a//b", "/aholo-lux3d/file",
                     "aholo-lux3d/aux?/test.txt", 'aholo-lux3d/a"b', "aholo-lux3d/file*"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Unsafe"):
                sync_release.read_archive(self.archive([name]))

    def test_archive_rejects_case_collisions_and_symlinks(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            sync_release.read_archive(self.archive(["aholo-lux3d/SKILL.md", "aholo-lux3d/skill.md"]))
        entry = zipfile.ZipInfo("aholo-lux3d/link")
        entry.create_system = 3
        entry.external_attr = (stat.S_IFLNK | 0o777) << 16
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            sync_release.read_archive(self.archive([entry]))

    def test_archive_rejects_file_directory_collisions(self):
        for names in (["aholo-lux3d/data", "aholo-lux3d/data/item.json"],
                      ["aholo-lux3d/Data/item.json", "aholo-lux3d/data"]):
            with self.subTest(names=names), self.assertRaisesRegex(ValueError, "collision"):
                sync_release.read_archive(self.archive(names))

    def test_reparse_point_is_rejected_without_is_junction_api(self):
        with mock.patch.object(Path, "lstat", return_value=SimpleNamespace(st_file_attributes=0x400)), \
                mock.patch.object(Path, "is_symlink", return_value=False):
            with self.assertRaisesRegex(ValueError, "Linked output path"):
                sync_release.safe_target(Path("output/reparse-check"))

    def test_sync_is_repeatable_and_check_is_read_only(self):
        result = self.initialize()
        self.assertEqual(46, result["commonFiles"])
        self.assertEqual("plugins/common/aholo-lux3d", result["skillPath"])
        before = {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mtime_ns)
                  for p in self.root.rglob("*") if p.is_file()}
        sync_release.sync(check=True)
        after = {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mtime_ns)
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        sync_release.sync()
        self.assertEqual({k: v[0] for k, v in before.items()},
                         {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_check_detects_runtime_tampering_and_extra_skill(self):
        self.initialize()
        path = self.root / sync_release.SKILL_PATH / "scripts/commerce.py"
        path.write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Distribution drift"):
            sync_release.sync(check=True)
        sync_release.sync()
        extra = self.root / sync_release.SKILL_PATH / "nested/SKILL.md"
        extra.parent.mkdir(parents=True)
        extra.write_text("unexpected")
        with self.assertRaisesRegex(ValueError, "Distribution drift"):
            sync_release.sync(check=True)

    def test_expanded_skill_contains_exact_common_zip_payload(self):
        self.initialize()
        expected = sync_release.read_archive(COMMON)[1]
        manifest = json.loads((self.root / "release-manifest.json").read_text())
        self.assertEqual("local-skill", manifest["distributionStatus"])
        self.assertNotIn("marketplace", manifest)
        skill = self.root / manifest["skill"]["path"]
        actual = {p.relative_to(skill).as_posix(): p.read_bytes() for p in skill.rglob("*") if p.is_file()}
        self.assertEqual(expected, actual)
        self.assertEqual(COMMON.read_bytes(), (self.root / manifest["archive"]["path"]).read_bytes())
        self.assertFalse(list(self.root.rglob("*.tar.gz")))

    def test_check_rejects_obsolete_codex_distribution(self):
        self.initialize()
        obsolete = self.root / "plugins/codex"
        obsolete.mkdir()
        with self.assertRaisesRegex(ValueError, "Obsolete Codex distribution"):
            sync_release.sync(check=True)
        self.assertTrue(obsolete.is_dir(), "Read-only checks must preserve obsolete paths")

    def test_invalid_provenance_fails_before_any_output_change(self):
        self.initialize()
        record = self.root / "lux3d-plugin/common/lux3d-plugin-1.1.0-common-skill.release.json"
        contents = json.loads(record.read_text())
        contents["sha256"] = "0" * 64
        record.write_text(json.dumps(contents))
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        with self.assertRaisesRegex(ValueError, "provenance"):
            sync_release.sync()
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})


if __name__ == "__main__":
    unittest.main()
