"""Validate Lux3D artifacts and build a secret-free delivery manifest."""

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import struct
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as element_tree


SUPPORTED_FORMATS = {
    "zip",
    "glb",
    "ply",
    "usdz",
    "obj_zip",
    "fbx_zip",
    "stl",
    "3mf",
}
OPERATIONS = {
    "image-to-3d",
    "text-to-3d",
    "material-transfer",
    "four-view",
    "export",
    "query",
    "list",
}
SECRET_KEYS = {
    "apikey",
    "authorization",
    "password",
    "secret",
    "accesskey",
    "accesskeyid",
    "accesskeysecret",
    "accesstoken",
    "oustoken",
    "ststoken",
    "securitytoken",
}
TRANSIENT_URL_KEYS = {
    "img",
    "imgs",
    "meshurl",
    "modelurl",
    "outputs",
    "sourceurl",
    "sourceurltemporary",
    "imageurl",
    "fourviewurls",
}
URL_WITH_QUERY_PATTERN = re.compile(r"(https?://[^?\s\"'<>]+)\?[^\s\"'<>]+", re.IGNORECASE)


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path, chunk_size=1024 * 1024):
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        while True:
            chunk = file_obj.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def normalize_secret_key(key):
    return re.sub(r"[^a-z0-9]", "", str(key).lower())


def assert_no_secrets(value, path="$"):
    if isinstance(value, dict):
        for key, child in value.items():
            if normalize_secret_key(key) in SECRET_KEYS:
                raise ValueError(f"Sensitive field is not allowed in delivery data: {path}.{key}")
            assert_no_secrets(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_secrets(child, f"{path}[{index}]")


def without_transient_urls(value):
    """Copy persistence data while dropping request and provider URL fields."""
    if isinstance(value, dict):
        return {
            key: without_transient_urls(child)
            for key, child in value.items()
            if normalize_secret_key(key) not in TRANSIENT_URL_KEYS
        }
    if isinstance(value, list):
        return [without_transient_urls(child) for child in value]
    if isinstance(value, str):
        return sanitize_error_message(value)
    return value


def sanitize_error_message(value):
    """Remove URL query strings before an exception is persisted."""
    if value is None:
        return None
    return URL_WITH_QUERY_PATTERN.sub(r"\1?<redacted>", str(value))


def infer_format(path):
    name = path.name.lower()
    if name.endswith(("_obj.zip", ".obj.zip", "obj.zip")):
        return "obj_zip"
    if name.endswith(("_fbx.zip", ".fbx.zip", "fbx.zip")):
        return "fbx_zip"
    if name.endswith(".usdz"):
        return "usdz"
    if name.endswith(".stl"):
        return "stl"
    if name.endswith(".3mf"):
        return "3mf"
    if name.endswith(".glb"):
        return "glb"
    if name.endswith(".ply"):
        return "ply"
    if name.endswith(".zip"):
        return "zip"
    raise ValueError(f"Cannot infer artifact format from filename: {path.name}")


def validate_path(file_path):
    path = pathlib.Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")
    if not path.is_file():
        raise ValueError(f"Artifact path is not a file: {path}")
    size = path.stat().st_size
    if size <= 0:
        raise ValueError(f"Artifact is empty: {path}")
    return path, size


def inspect_glb(path, size, require_embedded=False):
    with path.open("rb") as file_obj:
        header = file_obj.read(12)
        if len(header) != 12:
            raise ValueError("GLB header is truncated")
        magic, version, declared_length = struct.unpack("<4sII", header)
        if magic != b"glTF":
            raise ValueError("GLB magic must be glTF")
        if version != 2:
            raise ValueError(f"Unsupported GLB version: {version}")
        if declared_length != size:
            raise ValueError(
                f"GLB declared length {declared_length} does not match file size {size}"
            )
        chunk_header = file_obj.read(8)
        if len(chunk_header) != 8:
            raise ValueError("GLB JSON chunk header is missing")
        chunk_length, chunk_type = struct.unpack("<II", chunk_header)
        if chunk_type != 0x4E4F534A:
            raise ValueError("The first GLB chunk must be JSON")
        if 20 + chunk_length > size:
            raise ValueError("GLB JSON chunk exceeds the declared file length")
        json_bytes = file_obj.read(chunk_length)
        try:
            document = json.loads(json_bytes.rstrip(b" \t\r\n\x00").decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise ValueError("GLB JSON chunk is invalid") from exc
    if not isinstance(document, dict) or not isinstance(document.get("asset"), dict):
        raise ValueError("GLB JSON must be an object with an asset object")
    asset_version = document["asset"].get("version")
    if asset_version != "2.0":
        raise ValueError("GLB JSON asset.version must be 2.0")
    for field in ("scenes", "nodes", "meshes", "materials", "buffers", "images"):
        entries = document.get(field, [])
        if not isinstance(entries, list) or any(not isinstance(entry, dict) for entry in entries):
            raise ValueError(f"GLB {field} must be an array of objects")
    if require_embedded:
        for resource in document.get("buffers", []) + document.get("images", []):
            if "uri" in resource and (
                not isinstance(resource["uri"], str) or not resource["uri"].startswith("data:")
            ):
                raise ValueError("Offline GLB buffers and images must be embedded")
    return {
        "glbVersion": version,
        "assetVersion": asset_version,
        "scenes": len(document.get("scenes") or []),
        "nodes": len(document.get("nodes") or []),
        "meshes": len(document.get("meshes") or []),
        "materials": len(document.get("materials") or []),
    }


def _safe_zip_name(name):
    normalized = name.replace("\\", "/")
    if "\x00" in normalized:
        return False
    path = pathlib.PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts:
        return False
    if path.parts and re.match(r"^[A-Za-z]:$", path.parts[0]):
        return False
    return True


def inspect_zip(path, output_format):
    if not zipfile.is_zipfile(path):
        raise ValueError(f"{output_format} artifact is not a valid ZIP container")
    with zipfile.ZipFile(path, "r") as archive:
        infos = [info for info in archive.infolist() if not info.is_dir()]
        if not infos:
            raise ValueError(f"{output_format} archive contains no files")
        unsafe = [info.filename for info in infos if not _safe_zip_name(info.filename)]
        if unsafe:
            raise ValueError(f"Archive contains unsafe path: {unsafe[0]}")
        broken = archive.testzip()
        if broken:
            raise ValueError(f"Archive CRC check failed for: {broken}")
        names = [info.filename for info in infos]
        lower_names = [name.lower() for name in names]
        required_suffixes = {
            "zip": (".glb",),
            "obj_zip": (".obj",),
            "fbx_zip": (".fbx",),
            "usdz": (".usd", ".usda", ".usdc"),
        }[output_format]
        model_entries = [
            name
            for name, lower in zip(names, lower_names)
            if lower.endswith(required_suffixes)
        ]
        if not model_entries:
            expected = ", ".join(required_suffixes)
            raise ValueError(
                f"{output_format} archive is missing a model entry ({expected})"
            )
        if output_format == "usdz":
            compressed = [
                info.filename for info in infos if info.compress_type != zipfile.ZIP_STORED
            ]
            if compressed:
                raise ValueError("USDZ entries must be stored without ZIP compression")
    return {
        "zipEntries": len(infos),
        "modelEntries": model_entries[:20],
    }


def inspect_ply(path):
    with path.open("rb") as file_obj:
        header_bytes = file_obj.read(1024 * 1024)
    marker = b"end_header"
    marker_index = header_bytes.find(marker)
    if marker_index < 0:
        raise ValueError("PLY end_header was not found in the first MiB")
    header_slice = header_bytes[: marker_index + len(marker)]
    try:
        header = header_slice.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("PLY header must be ASCII") from exc
    lines = [line.strip() for line in header.replace("\r", "").split("\n")]
    if not lines or lines[0] != "ply":
        raise ValueError("PLY header must start with ply")
    format_lines = [line for line in lines if line.startswith("format ")]
    if len(format_lines) != 1:
        raise ValueError("PLY header must contain exactly one format declaration")
    parts = format_lines[0].split()
    if len(parts) != 3 or parts[1] not in {
        "ascii",
        "binary_little_endian",
        "binary_big_endian",
    }:
        raise ValueError("PLY format declaration is invalid")
    vertex_lines = [line for line in lines if line.startswith("element vertex ")]
    if len(vertex_lines) != 1:
        raise ValueError("PLY header must contain one vertex element")
    try:
        vertices = int(vertex_lines[0].split()[2])
    except (IndexError, ValueError) as exc:
        raise ValueError("PLY vertex count is invalid") from exc
    if vertices <= 0:
        raise ValueError("PLY must contain at least one vertex")
    return {"plyFormat": parts[1], "vertices": vertices}


def inspect_stl(path, size):
    """Perform bounded structural checks for binary or ASCII STL."""
    with path.open("rb") as file_obj:
        binary_header = file_obj.read(84)
    if len(binary_header) == 84:
        triangles = struct.unpack("<I", binary_header[80:84])[0]
        expected_size = 84 + triangles * 50
        if triangles > 0 and expected_size == size:
            return {"stlEncoding": "binary", "triangles": triangles}

    facets = 0
    saw_end = False
    with path.open("rb") as file_obj:
        first_line = file_obj.readline(4096).strip().lower()
        if not first_line.startswith(b"solid"):
            raise ValueError("STL is neither a complete binary STL nor an ASCII solid")
        for raw_line in file_obj:
            line = raw_line.strip().lower()
            if line.startswith(b"facet normal"):
                facets += 1
            elif line.startswith(b"endsolid"):
                saw_end = True
    if facets <= 0 or not saw_end:
        raise ValueError("ASCII STL must contain at least one facet and endsolid")
    return {"stlEncoding": "ascii", "triangles": facets}


def inspect_3mf(path):
    """Check the required ZIP package parts and model XML of a 3MF file."""
    if not zipfile.is_zipfile(path):
        raise ValueError("3mf artifact is not a valid ZIP container")
    with zipfile.ZipFile(path, "r") as archive:
        infos = [info for info in archive.infolist() if not info.is_dir()]
        unsafe = [info.filename for info in infos if not _safe_zip_name(info.filename)]
        if unsafe:
            raise ValueError(f"Archive contains unsafe path: {unsafe[0]}")
        broken = archive.testzip()
        if broken:
            raise ValueError(f"Archive CRC check failed for: {broken}")
        names = {info.filename.replace("\\", "/").lower(): info.filename for info in infos}
        if "[content_types].xml" not in names:
            raise ValueError("3mf package is missing [Content_Types].xml")
        model_names = [
            original
            for lower, original in names.items()
            if lower.startswith("3d/") and lower.endswith(".model")
        ]
        if not model_names:
            raise ValueError("3mf package is missing a 3D model part")
        try:
            root = element_tree.fromstring(archive.read(model_names[0]))
        except element_tree.ParseError as exc:
            raise ValueError("3mf model XML is invalid") from exc
        if root.tag.rsplit("}", 1)[-1].lower() != "model":
            raise ValueError("3mf model part must have a model root element")
    return {"zipEntries": len(infos), "modelPart": model_names[0]}


def inspect_artifact(file_path, format_hint=None, *, require_embedded_glb=False):
    path, size = validate_path(file_path)
    output_format = format_hint or infer_format(path)
    if output_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported artifact format: {output_format}")
    details = {}
    if output_format == "glb":
        details = inspect_glb(path, size, require_embedded=require_embedded_glb)
    elif output_format in {"zip", "usdz", "obj_zip", "fbx_zip"}:
        details = inspect_zip(path, output_format)
    elif output_format == "ply":
        details = inspect_ply(path)
    elif output_format == "stl":
        details = inspect_stl(path, size)
    elif output_format == "3mf":
        details = inspect_3mf(path)
    return {
        "path": str(path),
        "format": output_format,
        "size": size,
        "sha256": sha256_file(path),
        "validation": {"valid": True, **details},
    }


def integration_guidance(target_kind, formats):
    preferred = {
        "web": ["glb"],
        "unity": ["glb", "fbx_zip"],
        "unreal": ["fbx_zip", "glb"],
        "blender": ["glb", "fbx_zip", "obj_zip"],
        "dcc": ["glb", "fbx_zip", "obj_zip"],
        "apple-ar": ["usdz"],
        "editable-pbr": ["zip"],
        "geometry": ["ply", "stl"],
        "manufacturing": ["3mf", "stl"],
        "generic": ["glb", "zip"],
    }.get(target_kind, ["glb", "zip"])
    available_preferred = [item for item in preferred if item in formats]
    return {
        "targetKind": target_kind,
        "preferredAvailableFormats": available_preferred,
        "requiresTargetProjectVerification": True,
        "note": "Inspect and follow the target project's existing asset and loader conventions before integration.",
    }


def build_manifest(spec):
    if not isinstance(spec, dict):
        raise ValueError("Delivery spec must be a JSON object")
    assert_no_secrets(spec)
    spec = without_transient_urls(spec)
    operation = spec.get("operation")
    if operation not in OPERATIONS:
        raise ValueError("Delivery spec has an unsupported operation")
    region = spec.get("region")
    if region not in {"cn", "international"}:
        raise ValueError("Delivery spec region must be cn or international")
    task_id = spec.get("taskId")
    if task_id in (None, ""):
        raise ValueError("Delivery spec taskId is required")
    step_id = spec.get("stepId")
    attempt_id = spec.get("attemptId")
    if not isinstance(step_id, str) or not step_id:
        raise ValueError("Delivery spec stepId is required")
    if not isinstance(attempt_id, str) or not attempt_id:
        raise ValueError("Delivery spec attemptId is required")
    target = spec.get("target")
    if not isinstance(target, dict) or not str(target.get("kind") or "").strip():
        raise ValueError("Delivery spec target.kind is required")
    artifacts = spec.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("Delivery spec artifacts must be a non-empty list")
    inspected = []
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict) or not artifact.get("path"):
            raise ValueError(f"artifacts[{index}].path is required")
        item = inspect_artifact(artifact["path"], artifact.get("format"))
        item["artifactId"] = artifact.get(
            "artifactId", f"{step_id}:{attempt_id}:{index + 1}"
        )
        item["sourceStepId"] = step_id
        item["version"] = artifact.get("version", attempt_id)
        inspected.append(item)
    formats = [item["format"] for item in inspected]
    return {
        "schema": "lux3d.delivery/v2",
        "createdAt": utc_now(),
        "workflow": {
            "operation": operation,
            "region": region,
            "version": spec.get("version"),
            "taskId": str(task_id),
            "stepId": step_id,
            "attemptId": attempt_id,
        },
        "inputs": spec.get("inputs") or {},
        "artifacts": inspected,
        "target": target,
        "integration": integration_guidance(str(target["kind"]), formats),
    }


def write_json_atomic(path, payload):
    target = pathlib.Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent)
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as file_obj:
            json.dump(payload, file_obj, ensure_ascii=False, indent=2)
            file_obj.write("\n")
        os.replace(temporary, target)
    except Exception:
        if os.path.exists(temporary):
            os.remove(temporary)
        raise


def build_parser():
    parser = argparse.ArgumentParser(description="Validate and deliver Lux3D artifacts.")
    subparsers = parser.add_subparsers(dest="command")
    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("file_path")
    inspect_parser.add_argument("--format", choices=sorted(SUPPORTED_FORMATS))
    manifest = subparsers.add_parser("manifest")
    manifest.add_argument("--spec", required=True)
    manifest.add_argument("--output", required=True)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "inspect":
        result = inspect_artifact(args.file_path, args.format)
    elif args.command == "manifest":
        with open(args.spec, "r", encoding="utf-8") as file_obj:
            spec = json.load(file_obj)
        result = build_manifest(spec)
        write_json_atomic(args.output, result)
    else:
        parser.print_help()
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, RuntimeError, TimeoutError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
