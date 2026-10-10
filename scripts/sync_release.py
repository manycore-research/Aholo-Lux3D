"""Refresh or verify the maintained Common Skill source integrity record.

The historical ZIP is a record only; this command never reads or writes it.
Uses only Python's standard library. No installation, API calls or publishing.
Run with --check to verify the checkout without writing any files.

Author: yinjie.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = Path("plugins/common/aholo-lux3d")
LEGACY_PATHS = ("plugins/codex", "lux3d-plugin/codex", ".agents/plugins/marketplace.json")
MAX_BYTES = 256 * 1024 * 1024
DIGEST_PROTOCOL = "lux3d.entries/v1"


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def entries_digest(files):
    """Hash each path-length, content-length, path, content tuple using v1."""
    value = hashlib.sha256((DIGEST_PROTOCOL + "\0").encode("ascii"))
    for name, data in sorted(files.items()):
        name = name.encode("utf-8")
        value.update(len(name).to_bytes(8, "big"))
        value.update(len(data).to_bytes(8, "big"))
        value.update(name)
        value.update(data)
    return value.hexdigest()


def safe_target(relative):
    """Do not follow symlinks or Windows junctions in managed paths."""
    path = ROOT / relative
    path.resolve().relative_to(ROOT)
    cursor = ROOT
    for part in path.relative_to(ROOT).parts:
        cursor /= part
        try:
            attributes = getattr(cursor.lstat(), "st_file_attributes", 0)
        except FileNotFoundError:
            attributes = 0
        if cursor.is_symlink() or attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
            raise ValueError(f"Linked output path is not supported: {cursor}")
    return path


def validate_name(name):
    parts = PurePosixPath(name).parts
    if ("\\" in name or any(c in name for c in ':<>"|?*')
            or name.startswith("/") or any(p in ("", ".", "..") for p in name.split("/"))
            or any(p.endswith((".", " ")) or re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", p) for p in parts)
            or any(ord(c) < 32 for c in name)):
        raise ValueError(f"Unsafe or unsupported source path: {name}")


def tree_files(root):
    """Read regular source files without traversing linked directories."""
    if not root.is_dir():
        raise ValueError(f"Missing Common Skill source directory: {root}")
    result, seen, total = {}, set(), 0
    pending = [root]
    while pending:
        for path in pending.pop().iterdir():
            safe_target(path.relative_to(ROOT))
            name = path.relative_to(root).as_posix()
            validate_name(name)
            key = unicodedata.normalize("NFC", name).casefold()
            if key in seen:
                raise ValueError(f"Duplicate source path: {name}")
            seen.add(key)
            metadata = path.lstat()
            if stat.S_ISDIR(metadata.st_mode):
                pending.append(path)
            elif stat.S_ISREG(metadata.st_mode):
                total += metadata.st_size
                if metadata.st_size > 64 * 1024 * 1024 or total > MAX_BYTES:
                    raise ValueError("Skill source exceeds release size limits")
                result[name] = path.read_bytes()
            else:
                raise ValueError(f"Unsupported entry in Skill source: {name}")
    return result


def validate_skill(files):
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
    return build


def sync(common_archive=None, *, check=False):
    if common_archive is not None:
        raise ValueError("Archive import is no longer supported; maintain plugins/common/aholo-lux3d directly")
    manifest_path = safe_target(Path("release-manifest.json"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for relative in LEGACY_PATHS:
        if safe_target(Path(relative)).exists():
            raise ValueError(f"Obsolete Codex distribution must be removed before synchronization: {relative}")
    files = tree_files(safe_target(SKILL_PATH))
    build = validate_skill(files)
    build.update({
        "inputsDigest": entries_digest({n: data for n, data in files.items() if n != "build-info.json"}),
        "coreDigest": entries_digest({n: data for n, data in files.items()
                                      if n == "body.md" or n.startswith(("core/", "references/"))}),
        "inputsDigestSource": "github-skill-source-excluding-build-info",
        "coreDigestSource": "github-skill-source-core-body-references",
        "digestProtocol": DIGEST_PROTOCOL,
    })
    files["build-info.json"] = json_bytes(build)
    # Historical archive metadata is deliberately preserved without opening the archive.
    manifest["skill"].update({"name": "aholo-lux3d", "version": build["version"],
                              "path": SKILL_PATH.as_posix(), "identityMode": "automatic-host"})
    manifest["source"] = {"path": SKILL_PATH.as_posix(), "sha256": entries_digest(files),
                          "digestProtocol": DIGEST_PROTOCOL, "fileCount": len(files)}
    manifest["sharedCore"] = {"version": build["coreVersion"], "digest": build["coreDigest"],
                              "digestSource": build["coreDigestSource"]}
    expected = {SKILL_PATH / "build-info.json": files["build-info.json"],
                Path("release-manifest.json"): json_bytes(manifest)}
    for relative in expected:
        target = safe_target(relative)
        if not target.is_file():
            raise ValueError(f"Expected source metadata file: {relative}")
    differences = [relative.as_posix() for relative, data in expected.items()
                   if (ROOT / relative).read_bytes() != data]
    if check:
        if differences:
            raise ValueError("Source integrity drift: " + ", ".join(differences))
    else:
        for relative in differences:
            safe_target(Path(relative)).write_bytes(expected[Path(relative)])
    return {"valid": True, "checkOnly": check, "version": build["version"], "commonFiles": len(files),
            "skillPath": SKILL_PATH.as_posix(), "sourceSha256": manifest["source"]["sha256"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(sync(check=args.check), indent=2))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"Source verification failed: {exc}\n")


if __name__ == "__main__":
    main()
