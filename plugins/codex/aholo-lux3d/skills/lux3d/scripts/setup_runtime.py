#!/usr/bin/env python3
"""Prepare a private Python environment for the installed Lux3D Skill."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv


def python_path(directory):
    return directory / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def ready(python):
    if not python.is_file():
        return False
    return subprocess.run(
        [str(python), "-I", "-c", "import requests; requests.Session().close()"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def prepare(requirements, directory, *, check=False):
    python = python_path(directory)
    stamp = directory / ".lux3d-requirements.sha256"
    digest = hashlib.sha256(requirements.read_bytes()).hexdigest()
    current = stamp.is_file() and stamp.read_text().strip() == digest
    if current and ready(python):
        return python
    if check:
        raise RuntimeError("Run setup_runtime.py without --check to prepare dependencies.")
    if not python.is_file():
        # Prefer uv when available; otherwise use the standard venv/pip toolchain.
        venv.EnvBuilder(with_pip=shutil.which("uv") is None).create(directory)
    uv = shutil.which("uv")
    if not uv:
        pip_available = subprocess.run(
            [str(python), "-m", "pip", "--version"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        ).returncode == 0
        if not pip_available:
            subprocess.run([str(python), "-m", "ensurepip"], check=True, stdout=sys.stderr)
    command = (
        [uv, "pip", "install", "--python", str(python)]
        if uv else [str(python), "-m", "pip", "install"]
    )
    subprocess.run(command + ["-r", str(requirements)], check=True, stdout=sys.stderr)
    if not ready(python):
        raise RuntimeError("Dependency installation finished but the runtime import check failed.")
    stamp.write_text(digest + "\n")
    return python


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-dir", type=Path, help="Override the private environment directory.")
    parser.add_argument("--check", action="store_true", help="Check readiness without installing anything.")
    args = parser.parse_args()
    skill = Path(__file__).resolve().parents[1]
    requirements = skill / "core/runtime/requirements.txt"
    # Allow the maintained source entrypoint to be checked before packaging.
    repository = skill.parents[3]
    if not requirements.is_file() and (repository / "scripts/build-dist.mjs").is_file():
        requirements = repository / "shared/core/runtime/requirements.txt"
    directory = (args.env_dir or (
        Path.home() / ".cache/aholo-lux3d" /
        f"python-{sys.version_info.major}.{sys.version_info.minor}"
    )).expanduser().absolute()
    try:
        python = prepare(requirements, directory, check=args.check)
    except (OSError, RuntimeError, subprocess.CalledProcessError):
        print(json.dumps({"error": {
            "code": "CLI_DEPENDENCY_SETUP_REQUIRED",
            "message": "Lux3D Python dependencies are not ready. Run setup_runtime.py; check the installer output if setup fails.",
        }}), file=sys.stderr)
        return 1
    print(json.dumps({"status": "ready", "python": str(python)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
