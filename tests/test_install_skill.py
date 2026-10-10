"""Real isolated Common Skill installation and preservation checks.

Author: yinjie.
"""

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import shutil
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
        release = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(first["fileCount"], release["source"]["fileCount"])
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
        config = self.skills_dir / install_skill.INSTALLATION_CONFIG
        config.write_text('{"inviteCode":"original"}\n', encoding="utf-8")
        before = install_skill.snapshot(self.skills_dir)
        with self.assertRaisesRegex(ValueError, "nothing was overwritten"):
            install_skill.install(self.skills_dir, invite_code="replacement")
        self.assertEqual(before, install_skill.snapshot(self.skills_dir))

    def source_checkout(self):
        checkout = self.root / "checkout"
        shutil.copytree(ROOT / install_skill.sync_release.SKILL_PATH,
                        checkout / install_skill.sync_release.SKILL_PATH)
        shutil.copyfile(ROOT / "release-manifest.json", checkout / "release-manifest.json")
        return checkout

    def test_bad_release_rejected_before_creating_destination(self):
        checkout = self.source_checkout()
        with mock.patch.object(install_skill.sync_release, "ROOT", checkout):
            install_skill.sync_release.sync()
            body = checkout / install_skill.sync_release.SKILL_PATH / "body.md"
            body.write_bytes(body.read_bytes() + b"\nUnrecorded source change.\n")
            with self.assertRaisesRegex(ValueError, "Source integrity drift"):
                install_skill.install(self.skills_dir, invite_code="not-recorded")
        self.assertFalse(self.skills_dir.exists())

    def test_install_uses_latest_source_without_reading_historical_zip(self):
        checkout = self.source_checkout()
        release = json.loads((checkout / "release-manifest.json").read_text())
        historical = checkout / release["archive"]["path"]
        source = checkout / install_skill.sync_release.SKILL_PATH
        names = ("SKILL.md", "body.md", "references/review.md", "references/results.md")
        expected = {}
        for name in names:
            path = source / name
            expected[name] = path.read_bytes() + b"\nNew source guidance preserved.\n"
            path.write_bytes(expected[name])
        with mock.patch.object(install_skill.sync_release, "ROOT", checkout):
            install_skill.sync_release.sync()
            for state in ("missing", "corrupt"):
                with self.subTest(archive=state):
                    if state == "corrupt":
                        historical.parent.mkdir(parents=True)
                        historical.write_bytes(b"not a ZIP; only a historical record")
                    target = self.root / state / "skills"
                    result = install_skill.install(target)
                    installed = Path(result["path"])
                    self.assertEqual(install_skill.snapshot(source), install_skill.snapshot(installed))
                    for name in names:
                        self.assertEqual(expected[name], (installed / name).read_bytes())
            self.assertEqual(b"not a ZIP; only a historical record", historical.read_bytes())

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
        config = self.skills_dir / install_skill.INSTALLATION_CONFIG
        config.write_text('{"inviteCode":"original"}\n', encoding="utf-8")
        before = install_skill.snapshot(self.skills_dir)
        with mock.patch.object(Path, "write_bytes", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(OSError, "disk full"):
                install_skill.install(self.skills_dir, invite_code="replacement")
        self.assertEqual(before, install_skill.snapshot(self.skills_dir))
        self.assertEqual((keep / "keep.txt").read_text(encoding="utf-8"), "keep")

    def test_install_with_invite_code_keeps_release_unchanged_and_output_private(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = install_skill.main(["--skills-dir", str(self.skills_dir), "--invite-code", "  邀请-code-001  "])
        self.assertEqual(code, 0, stderr.getvalue())
        result = json.loads(stdout.getvalue())
        config = self.skills_dir / install_skill.INSTALLATION_CONFIG
        self.assertEqual(Path(result["installationConfigPath"]), config)
        self.assertTrue(config.is_absolute())
        self.assertEqual(json.loads(config.read_text(encoding="utf-8")), {"inviteCode": "邀请-code-001"})
        self.assertNotIn("邀请-code-001", stdout.getvalue() + stderr.getvalue())
        installed = Path(result["path"])
        source = install_skill.sync_release.ROOT / install_skill.sync_release.SKILL_PATH
        self.assertEqual(install_skill.snapshot(installed), install_skill.snapshot(source))
        self.assertEqual(set(self.skills_dir.iterdir()), {installed, config})

    def test_identical_install_can_add_and_update_invite_code(self):
        first = install_skill.install(self.skills_dir)
        installed = Path(first["path"])
        before = {str(p): (p.read_bytes(), p.stat().st_mtime_ns)
                  for p in installed.rglob("*") if p.is_file()}
        config = self.skills_dir / install_skill.INSTALLATION_CONFIG
        for value in ("first-code", "second-code"):
            with self.subTest(value=value):
                result = install_skill.install(self.skills_dir, invite_code=value)
                self.assertTrue(result["unchanged"])
                self.assertEqual(json.loads(config.read_text(encoding="utf-8")), {"inviteCode": value})
                self.assertEqual(before, {str(p): (p.read_bytes(), p.stat().st_mtime_ns)
                                          for p in installed.rglob("*") if p.is_file()})

    def test_missing_invite_code_preserves_existing_config_without_reading_it(self):
        self.skills_dir.mkdir()
        config = self.skills_dir / install_skill.INSTALLATION_CONFIG
        config.write_text("preserve existing bytes, even malformed JSON", encoding="utf-8")
        before = (config.read_bytes(), config.stat().st_mtime_ns)
        first = install_skill.install(self.skills_dir)
        self.assertFalse(first["unchanged"])
        second = install_skill.install(self.skills_dir)
        self.assertTrue(second["unchanged"])
        self.assertNotIn("installationConfigPath", second)
        self.assertEqual(before, (config.read_bytes(), config.stat().st_mtime_ns))

    def test_reinstall_preserves_or_explicitly_updates_invite_code(self):
        first = install_skill.install(self.skills_dir, invite_code="initial-code")
        installed = Path(first["path"])
        config = self.skills_dir / install_skill.INSTALLATION_CONFIG
        before = (config.read_bytes(), config.stat().st_mtime_ns)
        installed.rename(self.root / "removed-installation")
        result = install_skill.install(self.skills_dir)
        self.assertFalse(result["unchanged"])
        self.assertEqual(before, (config.read_bytes(), config.stat().st_mtime_ns))
        installed.rename(self.root / "removed-again")
        result = install_skill.install(self.skills_dir, invite_code="new-code")
        self.assertFalse(result["unchanged"])
        self.assertEqual(json.loads(config.read_text(encoding="utf-8")), {"inviteCode": "new-code"})

    def test_invalid_invite_code_fails_without_writes_or_echoing_value(self):
        invalid = ("", "  ", "x" * 256, "bad\x00code", "\nbad-code", "bad\tcode",
                   "bad\x7fcode", "bad\x85code", "bad\x9fcode")
        for value in invalid:
            with self.subTest(value=repr(value)):
                stdout, stderr = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    code = install_skill.main(["--skills-dir", str(self.skills_dir), "--invite-code", value])
                self.assertEqual(code, 1)
                self.assertEqual(stdout.getvalue(), "")
                self.assertEqual(json.loads(stderr.getvalue()), {
                    "ok": False,
                    "error": "Invite code must be a nonblank string of at most 255 characters without control characters",
                })
                self.assertFalse(self.skills_dir.exists())
        for value in (123, {}, []):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "Invite code must"):
                install_skill.install(self.skills_dir, invite_code=value)
        self.assertFalse(self.skills_dir.exists())

    def test_invite_code_length_limit_applies_after_trimming(self):
        value = "码" * 255
        install_skill.install(self.skills_dir, invite_code="  " + value + "  ")
        config = self.skills_dir / install_skill.INSTALLATION_CONFIG
        self.assertEqual(json.loads(config.read_text(encoding="utf-8")), {"inviteCode": value})

    def test_failed_config_replacement_preserves_old_config_and_removes_temporary_file(self):
        install_skill.install(self.skills_dir, invite_code="original")
        config = self.skills_dir / install_skill.INSTALLATION_CONFIG
        before = install_skill.snapshot(self.skills_dir)
        with mock.patch.object(os, "replace", side_effect=OSError("replacement denied")):
            with self.assertRaisesRegex(OSError, "replacement denied"):
                install_skill.install(self.skills_dir, invite_code="replacement")
        self.assertEqual(before, install_skill.snapshot(self.skills_dir))
        self.assertEqual(json.loads(config.read_text(encoding="utf-8")), {"inviteCode": "original"})

    def test_linked_config_is_rejected_before_installation(self):
        self.skills_dir.mkdir()
        config = self.skills_dir / install_skill.INSTALLATION_CONFIG
        config.write_text('{"inviteCode":"original"}', encoding="utf-8")
        real_lstat = Path.lstat
        def lstat(path, *args, **kwargs):
            if path == config:
                return type("ReparseMetadata", (), {"st_mode": 0o100644, "st_file_attributes": 0x400})()
            return real_lstat(path, *args, **kwargs)
        with mock.patch.object(Path, "lstat", lstat):
            with self.assertRaisesRegex(ValueError, "Linked installation path"):
                install_skill.install(self.skills_dir, invite_code="replacement")
        self.assertEqual(list(self.skills_dir.iterdir()), [config])
        self.assertEqual(json.loads(config.read_text(encoding="utf-8")), {"inviteCode": "original"})


if __name__ == "__main__":
    unittest.main()
