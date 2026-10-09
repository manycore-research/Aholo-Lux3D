"""Install the verified Common Skill into an explicitly chosen local Skill directory.

Only Python's standard library is used. This copies the complete release without
changing host settings, downloading dependencies, or contacting Lux3D.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import zipfile

import sync_release


SKILL_NAME = "aholo-lux3d"


def contained(path, root):
    return path == root or root in path.parents


def unlinked(path):
    """Check lexical ancestors before resolving, including Windows junctions."""
    absolute = Path(os.path.abspath(os.fspath(path)))
    for cursor in reversed((absolute, *absolute.parents)):
        try:
            metadata = cursor.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(metadata.st_mode) or getattr(metadata, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Linked installation path is not supported: {cursor}")
    return absolute.resolve()


def snapshot(root):
    """Read regular files and directory names without following linked entries."""
    root = unlinked(root)
    if not root.is_dir():
        raise ValueError(f"Expected a Skill directory: {root}")
    files, directories = {}, set()
    pending = [root]
    while pending:
        parent = pending.pop()
        for child in parent.iterdir():
            unlinked(child)
            relative = child.relative_to(root).as_posix()
            mode = child.lstat().st_mode
            if stat.S_ISDIR(mode):
                directories.add(relative)
                pending.append(child)
            elif stat.S_ISREG(mode):
                files[relative] = child.read_bytes()
            else:
                raise ValueError(f"Unsupported entry in Skill directory: {child}")
    return files, directories


def destination(skills_dir):
    parent = unlinked(skills_dir)
    target = unlinked(parent / SKILL_NAME)
    repository = sync_release.ROOT.resolve()
    source = repository / sync_release.SKILL_PATH
    # A repository's output directory is reserved for disposable validation.
    # Production installs belong outside the distribution checkout.
    if (contained(source, target) or contained(target, source)
            or contained(repository, target)
            or (contained(target, repository) and not contained(target, repository / "output"))):
        raise ValueError("Installation destination overlaps the distribution repository")
    if target.parent != parent:
        raise ValueError("Installation destination must remain within the chosen Skill directory")
    if parent.exists() and not parent.is_dir():
        raise ValueError(f"Skill parent is not a directory: {parent}")
    return parent, target


def cleanup_staging(staging, parent):
    """Remove only our temporary directory, after checking every deletion path."""
    checked = unlinked(staging)
    if checked.parent != unlinked(parent) or not checked.name.startswith(".aholo-lux3d-install-"):
        raise ValueError("Refusing to clean up an unexpected staging path")
    snapshot(checked)
    shutil.rmtree(checked)


def install(skills_dir):
    release = sync_release.sync(check=True)
    source = sync_release.ROOT / sync_release.SKILL_PATH
    expected = snapshot(source)
    parent, target = destination(skills_dir)
    result = {
        "name": SKILL_NAME,
        "version": release["version"],
        "path": str(target),
        "fileCount": len(expected[0]),
        "unchanged": False,
    }
    if target.exists():
        if snapshot(target) != expected:
            raise ValueError(f"Existing Skill differs; nothing was overwritten: {target}")
        result["unchanged"] = True
        return result

    parent.mkdir(parents=True, exist_ok=True)
    unlinked(parent)
    staging = Path(tempfile.mkdtemp(prefix=".aholo-lux3d-install-", dir=parent))
    try:
        for relative in sorted(expected[1]):
            (staging / relative).mkdir(parents=True, exist_ok=True)
        for relative, payload in expected[0].items():
            (staging / relative).write_bytes(payload)
        if snapshot(staging) != expected:
            raise ValueError("Installation staging verification failed")
        unlinked(target)
        if target.exists():
            raise ValueError(f"Skill appeared during installation; nothing was overwritten: {target}")
        # Windows rename fails if the destination exists. The explicit check
        # above also rejects existing directories on other supported hosts.
        staging.rename(target)
        staging = None
    finally:
        if staging is not None:
            cleanup_staging(staging, parent)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=Path, required=True,
                        help="Explicit parent directory recognized by the host for local Skills")
    args = parser.parse_args(argv)
    try:
        result = install(args.skills_dir)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
