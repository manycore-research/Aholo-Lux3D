"""Real isolated Common Skill installation and preservation checks."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("install_skill", ROOT / "scripts/install_skill.py")
install_skill = importlib.util.module_from_spec(spec)
spec.loader.exec_module(install_skill)


class SkillInstallationTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / "output/install-tests"
        scratch.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.skills_dir = self.root / "skills"

    def test_complete_install_and_idempotent_repeat(self):
        first = install_skill.install(self.skills_dir)
        installed = Path(first["path"])
        source = install_skill.sync_release.ROOT / install_skill.sync_release.SKILL_PATH
        self.assertEqual(install_skill.snapshot(installed), install_skill.snapshot(source))
        self.assertEqual(first["fileCount"], 46)
        self.assertFalse(first["unchanged"])
        before = {str(p): p.stat().st_mtime_ns for p in installed.rglob("*")}
        second = install_skill.install(self.skills_dir)
        self.assertTrue(second["unchanged"])
        self.assertEqual(before, {str(p): p.stat().st_mtime_ns for p in installed.rglob("*")})
        self.assertEqual(list(self.skills_dir.iterdir()), [installed])

    def test_installed_identity_helper_resolves_packaged_resources_from_other_cwd(self):
        result = install_skill.install(self.skills_dir)
        helper = Path(result["path"]) / "scripts/host_identity.py"
        environment = dict(os.environ)
        for key in ("CODEX_THREAD_ID", "CLAUDECODE", "LUX3D_HOST_NAME"):
            environment.pop(key, None)
        completed = subprocess.run(
            [sys.executable, "-B", str(helper), "detect", "--host-name", "WorkBuddy"],
            cwd=self.root, env=environment, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        identity = json.loads(completed.stdout)
        self.assertEqual(identity["source"], 4)
        self.assertEqual(identity["agentName"], "workbuddy")

    def test_conflict_preserves_existing_files_and_other_skills(self):
        target = self.skills_dir / "aholo-lux3d"
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text("my customized skill", encoding="utf-8")
        other = self.skills_dir / "another-skill"
        other.mkdir()
        (other / "SKILL.md").write_text("unrelated", encoding="utf-8")
        before = install_skill.snapshot(self.skills_dir)
        with self.assertRaisesRegex(ValueError, "nothing was overwritten"):
            install_skill.install(self.skills_dir)
        self.assertEqual(before, install_skill.snapshot(self.skills_dir))

    def test_bad_release_rejected_before_creating_destination(self):
        checkout = self.root / "checkout"
        checkout.mkdir()
        archive = ROOT / "lux3d-plugin/common/lux3d-plugin-1.1.0-common-skill.zip"
        with mock.patch.object(install_skill.sync_release, "ROOT", checkout):
            install_skill.sync_release.sync(archive)
            skill = checkout / install_skill.sync_release.SKILL_PATH
            (skill / "SKILL.md").write_text("changed after synchronization", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Distribution drift"):
                install_skill.install(self.skills_dir)
        self.assertFalse(self.skills_dir.exists())

    def test_repository_and_source_destinations_rejected(self):
        for parent in (ROOT, ROOT / "plugins/common", ROOT / "scripts",
                       ROOT / "plugins/common/aholo-lux3d/skills"):
            with self.subTest(parent=parent), self.assertRaisesRegex(ValueError, "overlaps"):
                install_skill.destination(parent)

    def test_reparse_point_is_rejected(self):
        real_lstat = Path.lstat
        def lstat(path, *args, **kwargs):
            if path == self.skills_dir:
                return type("ReparseMetadata", (), {"st_mode": 0o040755, "st_file_attributes": 0x400})()
            return real_lstat(path, *args, **kwargs)
        with mock.patch.object(Path, "lstat", lstat):
            with self.assertRaisesRegex(ValueError, "Linked installation path"):
                install_skill.destination(self.skills_dir)

    def test_failed_copy_cleans_only_own_staging(self):
        self.skills_dir.mkdir()
        keep = self.skills_dir / ".aholo-lux3d-install-existing"
        keep.mkdir()
        (keep / "keep.txt").write_text("keep", encoding="utf-8")
        with mock.patch.object(Path, "write_bytes", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(OSError, "disk full"):
                install_skill.install(self.skills_dir)
        self.assertEqual(list(self.skills_dir.iterdir()), [keep])
        self.assertEqual((keep / "keep.txt").read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
