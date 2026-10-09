"""Synchronize the verified Common Skill archive for local installation in any supported host.

Uses only Python's standard library. No installation, API calls or publishing.
Run with --check to verify the checkout without writing any files.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import unicodedata
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = Path("plugins/common/aholo-lux3d")
LEGACY_PATHS = ("plugins/codex", "lux3d-plugin/codex", ".agents/plugins/marketplace.json")
COMMON_PREFIX = "aholo-lux3d/"
MAX_BYTES = 256 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_archive(path):
    """Validate checksum and portable paths before extracting anything."""
    payload = path.read_bytes()
    checksum = path.with_suffix(path.suffix + ".sha256").read_text(encoding="utf-8").split()
    if len(checksum) != 2 or checksum[1].lstrip("*") != path.name or checksum[0] != digest(payload):
        raise ValueError(f"Archive checksum mismatch: {path.name}")
    files, seen, total = {}, set(), 0
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for entry in archive.infolist():
            # ZipInfo normalizes Windows separators and truncates at NUL;
            # validate the original spelling, before that normalization.
            name = entry.orig_filename
            parts = PurePosixPath(name).parts
            if (not name.startswith(COMMON_PREFIX) or "\\" in name or any(c in name for c in ':<>"|?*')
                    or name.startswith("/") or any(p in ("", ".", "..") for p in name.split("/"))
                    or any(p.endswith((".", " ")) or re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", p) for p in parts)
                    or any(ord(c) < 32 for c in name) or entry.is_dir()
                    or stat.S_IFMT(entry.external_attr >> 16) not in (0, stat.S_IFREG)):
                raise ValueError(f"Unsafe or unsupported archive entry: {name}")
            key = unicodedata.normalize("NFC", name).casefold()
            if key in seen:
                raise ValueError(f"Duplicate archive entry: {name}")
            seen.add(key)
            total += entry.file_size
            if entry.file_size > 64 * 1024 * 1024 or total > MAX_BYTES:
                raise ValueError("Archive exceeds release size limits")
            files[name[len(COMMON_PREFIX):]] = archive.read(entry)
    for name in seen:
        if any(parent.as_posix() in seen for parent in PurePosixPath(name).parents):
            raise ValueError(f"Archive file/directory collision: {name}")
    return payload, files


def safe_target(relative):
    """Do not follow symlinks or Windows junctions in managed output paths."""
    path = ROOT / relative
    path.resolve().relative_to(ROOT)
    cursor = ROOT
    for part in path.relative_to(ROOT).parts:
        cursor /= part
        try:
            attributes = getattr(cursor.lstat(), "st_file_attributes", 0)
        except FileNotFoundError:
            attributes = 0
        # lstat works on Python 3.10/3.11 as well as hosts with is_junction().
        if cursor.is_symlink() or attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
            raise ValueError(f"Linked output path is not supported: {cursor}")
    return path


def tree_files(root):
    result = {}
    if root.exists():
        for path in root.rglob("*"):
            safe_target(path.relative_to(ROOT))
            if path.is_file():
                result[path.relative_to(root).as_posix()] = path.read_bytes()
    return result


def sync(common_archive=None, *, check=False):
    if common_archive is None:
        current = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))
        common_archive = safe_target(Path(current["archive"]["path"]))
    common_archive = Path(common_archive)
    archive_bytes, files = read_archive(common_archive)
    build = json.loads(files["build-info.json"])
    adapter = json.loads(files["adapter.json"])
    version = build["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Expected a semantic release version")
    if (adapter.get("schema") != "lux3d.ecosystem-adapter/v1"
            or adapter.get("version") != version or adapter.get("ecosystem") != "common"
            or adapter.get("distribution") != "skill"
            or adapter.get("identityMode") != "automatic-host" or "source" in adapter
            or build.get("releaseUnit") != "common" or build.get("mode") != "skill"
            or build.get("identityMode") != "automatic-host" or "source" in build):
        raise ValueError("Expected an automatic-host Common Skill release")
    if sorted(n for n in files if n.endswith("SKILL.md")) != ["SKILL.md"]:
        raise ValueError("Common must contain exactly one root Skill")
    if not re.search(r"^name: aholo-lux3d\s*$", files["SKILL.md"].decode("utf-8"), re.MULTILINE):
        raise ValueError("Common Skill name must be aholo-lux3d")
    for name in ("body.md", "scripts/commerce.py", "scripts/setup_runtime.py", "scripts/host_identity.py",
                 "host-identity.json", "release-contract.json", "agents/openai.yaml", "icon.png",
                 "core/runtime/requirements.txt", "core/runtime/lux3d_client.py", "core/viewer/viewer.bundle.js"):
        if name not in files:
            raise ValueError(f"Missing Common Skill resource: {name}")
    if any(n.startswith((".codex-plugin/", ".claude-plugin/")) for n in files):
        raise ValueError("Common Skill must not contain a host-specific plugin wrapper")
    registry = json.loads(files["host-identity.json"])
    if (registry.get("schema") != "lux3d.host-identity/v1"
            or {name: value["source"] for name, value in registry["knownHosts"].items()}
            != {"codex": 1, "claude-code": 2, "deepseek": 3, "workbuddy": 4}
            or registry.get("fallback") != {"source": 100, "agentName": "detected-host-name"}):
        raise ValueError("Invalid Common host identity registry")
    record_bytes = common_archive.with_suffix(".release.json").read_bytes()
    record = json.loads(record_bytes)
    if (record.get("schema") != "lux3d.release-artifact/v1"
            or record.get("filename") != common_archive.name or record.get("sha256") != digest(archive_bytes)
            or record.get("version") != version or record.get("buildInfo") != build
            or record.get("releaseUnit") != "common" or record.get("mode") != "skill"):
        raise ValueError("Common release provenance does not match its archive")
    archive_path = Path(f"lux3d-plugin/common/lux3d-plugin-{version}-common-skill.zip")
    if common_archive.name != archive_path.name:
        raise ValueError(f"Expected archive name: {archive_path.name}")
    checksum_path = archive_path.with_suffix(".zip.sha256")
    record_path = archive_path.with_suffix(".release.json")
    manifest = {
        "schemaVersion": "aholo-lux3d-common-skill/v1",
        "distributionRepository": "https://github.com/manycore-research/Aholo-Lux3D",
        "distributionStatus": "local-skill",
        "agentEntrypoint": "AGENTS.md",
        "agentEntrypointURL": "https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md",
        "gitRef": "master",
        "skill": {"name": "aholo-lux3d", "displayName": "Aholo Lux3D", "version": version,
                  "path": SKILL_PATH.as_posix(), "identityMode": "automatic-host"},
        "archive": {"path": archive_path.as_posix(), "sha256": digest(archive_bytes),
                    "checksumPath": checksum_path.as_posix(), "releaseRecordPath": record_path.as_posix(),
                    "fileCount": len(files)},
        "installation": {"mode": "local-skill", "directoryName": "aholo-lux3d",
                         "helper": "scripts/install_skill.py", "hostIdentityRegistry": "host-identity.json",
                         "requires": ["local-skills", "python>=3.10", "filesystem", "https", "credential-injection"]},
        "sites": {"china": "https://lux3d.aholo3d.cn", "international": "https://lux3d.aholo3d.com"},
        "sharedCore": {"version": build["coreVersion"], "digest": build["coreDigest"],
                       "digestSource": "upstream-build-info"},
        "validation": {"upstreamHostValidated": build.get("hostValidated", False), "liveServiceValidated": False,
                       "note": "Local copy and offline checks do not establish acceptance in every host or paid generation."},
    }
    expected = {SKILL_PATH / name: data for name, data in files.items()}
    expected.update({archive_path: archive_bytes, record_path: record_bytes,
                     checksum_path: f"{digest(archive_bytes)}  {archive_path.name}\n".encode(),
                     Path("release-manifest.json"): json_bytes(manifest)})
    for relative in LEGACY_PATHS:
        if safe_target(Path(relative)).exists():
            raise ValueError(f"Obsolete Codex distribution must be removed before synchronization: {relative}")
    actual = tree_files(safe_target(SKILL_PATH))
    stale = [SKILL_PATH / name for name in actual.keys() - files.keys()]
    for path in (*expected, *stale):
        target = safe_target(path)
        if target.is_dir() or any(parent.exists() and not parent.is_dir() for parent in target.parents):
            raise ValueError(f"Output file/directory collision: {path}")
    differences = [path.as_posix() for path, data in expected.items()
                   if not (ROOT / path).is_file() or (ROOT / path).read_bytes() != data]
    if check:
        if differences or stale:
            raise ValueError("Distribution drift: " + ", ".join(differences + [p.as_posix() for p in stale]))
    else:
        for path in stale:
            safe_target(path).unlink()
        for path, data in expected.items():
            target = safe_target(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        for path in sorted((ROOT / SKILL_PATH).rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                safe_target(path.relative_to(ROOT)).rmdir()
    return {"valid": True, "checkOnly": check, "version": version, "commonFiles": len(files),
            "skillPath": SKILL_PATH.as_posix(), "commonSha256": digest(archive_bytes)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--common-archive", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(sync(args.common_archive, check=args.check), indent=2))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"Release sync failed: {exc}\n")


if __name__ == "__main__":
    main()
