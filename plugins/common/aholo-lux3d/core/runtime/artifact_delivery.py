"""Validate Lux3D artifacts and build a secret-free delivery manifest."""

import argparse
import base64
import datetime
import hashlib
import json
import math
import os
import pathlib
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as element_tree


# Compatibility tolerance from Khronos glTF-Validator, not a glTF specification limit.
# https://github.com/KhronosGroup/glTF-Validator/blob/602c54043ba66856b2e68c40fdf2bced975cdb8a/lib/src/errors.dart#L36
GLTF_VALIDATOR_QUATERNION_TOLERANCE = 0.00769
SUPPORTED_FORMATS = {
    "file",
    "obj",
    "zip",
    "glb",
    "ply",
    "usdz",
    "obj_zip",
    "fbx_zip",
    "fbx",
    "stl",
    "3mf",
}
OPERATIONS = {
    "articulation-animation",
    "mesh-retopology",
    "image-to-3d",
    "text-to-3d",
    "material-transfer",
    "four-view",
    "export",
    "auto-rig",
    "animation-retarget",
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
    "glburl",
    "artifacturl",
    "img",
    "imgs",
    "meshurl",
    "modelurl",
    "rigmodelurl",
    "animationglburl",
    "fbxurl",
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
    if name.endswith(".obj"):
        return "obj"
    if name.endswith(".glb"):
        return "glb"
    if name.endswith(".fbx"):
        return "fbx"
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


def inspect_glb(path, size, require_embedded=False, *, require_rig=False,
                require_animation=False, minimum_animation_clips=1):
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
        binary = b""
        if require_rig or require_animation:
            while file_obj.tell() < size:
                chunk_header = file_obj.read(8)
                if len(chunk_header) != 8:
                    raise ValueError("GLB chunk header is truncated")
                length, kind = struct.unpack("<II", chunk_header)
                chunk = file_obj.read(length)
                if len(chunk) != length or length % 4:
                    raise ValueError("GLB binary chunk is truncated or misaligned")
                if kind == 0x004E4942:
                    if binary:
                        raise ValueError("GLB has duplicate binary chunks")
                    binary = chunk
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
    details = {
        "glbVersion": version,
        "assetVersion": asset_version,
        "scenes": len(document.get("scenes") or []),
        "nodes": len(document.get("nodes") or []),
        "meshes": len(document.get("meshes") or []),
        "materials": len(document.get("materials") or []),
    }
    if require_rig or require_animation:
        details.update(_inspect_glb_character(document, binary, require_animation,
                                              minimum_animation_clips))
    return details


def _glb_index(entries, index, field):
    if type(index) is not int or not 0 <= index < len(entries):
        raise ValueError(f"GLB {field} reference is invalid")
    return entries[index]


def _glb_buffers(document, binary):
    buffers = []
    for index, entry in enumerate(document.get("buffers", [])):
        length = entry.get("byteLength")
        if type(length) is not int or length <= 0:
            raise ValueError("GLB buffer.byteLength is invalid")
        uri = entry.get("uri")
        if uri is None and index == 0:
            content = binary
        elif isinstance(uri, str) and uri.startswith("data:") and ";base64," in uri:
            try:
                content = base64.b64decode(uri.split(",", 1)[1], validate=True)
            except ValueError as exc:
                raise ValueError("GLB data buffer is invalid") from exc
        else:
            raise ValueError("Digital-human GLB buffers must be embedded")
        if not length <= len(content) <= length + 3:
            raise ValueError("GLB buffer length does not match readable data")
        buffers.append(content[:length])
    return buffers


def _glb_accessor(document, buffers, index, *, normalize=True):
    entry = _glb_index(document.get("accessors", []), index, "accessor")
    formats = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}
    components = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
    count, kind, component = entry.get("count"), entry.get("type"), entry.get("componentType")
    if (type(count) is not int or count <= 0 or not isinstance(kind, str) or kind not in components
            or type(component) is not int or component not in formats):
        raise ValueError("GLB accessor type, count or componentType is invalid")
    if kind == "MAT4" and component != 5126:
        raise ValueError("GLB inverse bind matrices must contain floats")
    def read_values(view_index, offset, count, component, width, *, sparse=False):
        view = _glb_index(document.get("bufferViews", []), view_index, "bufferView")
        extensions = view.get("extensions", {})
        if not isinstance(extensions, dict) or "EXT_meshopt_compression" in extensions:
            raise ValueError("Compressed digital-human GLB buffer data cannot be inspected")
        if sparse and "byteStride" in view:
            raise ValueError("GLB sparse bufferView must not define byteStride")
        data = _glb_index(buffers, view.get("buffer"), "buffer")
        start, length = view.get("byteOffset", 0), view.get("byteLength")
        component_size = struct.calcsize("<" + formats[component])
        stride = view.get("byteStride", width * component_size)
        if (any(type(value) is not int for value in (start, length, offset, stride))
                or min(start, offset) < 0 or length <= 0 or stride < width * component_size
                or (start + offset) % component_size or start + length > len(data)
                or offset + (count - 1) * stride + width * component_size > length
                or "byteStride" in view and (not 4 <= stride <= 252 or stride % 4)):
            raise ValueError("GLB accessor exceeds its readable or aligned bufferView")
        return [struct.unpack_from("<" + formats[component] * width, data,
                                    start + offset + row * stride) for row in range(count)]

    if "bufferView" in entry:
        values = read_values(entry["bufferView"], entry.get("byteOffset", 0), count, component, components[kind])
    elif entry.get("byteOffset", 0) == 0:
        values = [(0,) * components[kind] for _ in range(count)]
    else:
        raise ValueError("GLB accessor without bufferView must not define byteOffset")
    if "sparse" in entry:
        sparse = entry["sparse"]
        if not isinstance(sparse, dict) or type(sparse.get("count")) is not int or not 1 <= sparse["count"] <= count:
            raise ValueError("GLB sparse accessor count is invalid")
        indices, replacements = sparse.get("indices"), sparse.get("values")
        if (not isinstance(indices, dict) or not isinstance(replacements, dict)
                or type(indices.get("componentType")) is not int or indices["componentType"] not in {5121, 5123, 5125}):
            raise ValueError("GLB sparse accessor indices or values are invalid")
        indices = read_values(indices.get("bufferView"), indices.get("byteOffset", 0), sparse["count"],
                              indices["componentType"], 1, sparse=True)
        replacements = read_values(replacements.get("bufferView"), replacements.get("byteOffset", 0),
                                   sparse["count"], component, components[kind], sparse=True)
        previous = -1
        for (position,), replacement in zip(indices, replacements):
            if not previous < position < count:
                raise ValueError("GLB sparse indices must increase and stay within accessor count")
            values[position] = replacement
            previous = position
    normalized = entry.get("normalized", False)
    if type(normalized) is not bool or normalized and component in {5125, 5126}:
        raise ValueError("GLB accessor normalized flag is invalid")
    if normalized and normalize:
        denominator = {5120: 127, 5121: 255, 5122: 32767, 5123: 65535}[component]
        values = [tuple(max(value / denominator, -1.0) for value in row) for row in values]
    if any(not math.isfinite(value) for row in values for value in row):
        raise ValueError("GLB accessor contains non-finite data")
    return entry, values


def _inspect_glb_character(document, binary, require_animation, minimum_animation_clips):
    # glTF 2.0 skin references and vertex influences, not presence-only checks.
    # https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#skins
    for field in ("skins", "accessors", "bufferViews"):
        entries = document.get(field, [])
        if not isinstance(entries, list) or any(not isinstance(value, dict) for value in entries):
            raise ValueError(f"GLB {field} must be an array of objects")
    nodes, skins, meshes = document.get("nodes", []), document.get("skins", []), document.get("meshes", [])
    if "scene" in document:
        _glb_index(document.get("scenes", []), document["scene"], "default scene")
    buffers = _glb_buffers(document, binary)
    parents = [None] * len(nodes)
    for parent, node in enumerate(nodes):
        children = node.get("children", [])
        if not isinstance(children, list):
            raise ValueError("GLB node.children must be node references")
        for child in children:
            _glb_index(nodes, child, "child node")
            if parents[child] is not None:
                raise ValueError("GLB node has multiple parents")
            parents[child] = parent
    roots = [index for index, parent in enumerate(parents) if parent is None]
    pending, visited = list(roots), set()
    while pending:
        index = pending.pop()
        visited.add(index)
        pending.extend(nodes[index].get("children", []))
    if len(visited) != len(nodes):
        raise ValueError("GLB node hierarchy contains a cycle")

    def ancestors(index):
        result = set()
        while index is not None:
            result.add(index)
            index = parents[index]
        return result

    scenes = []
    for scene in document.get("scenes", []):
        pending = scene.get("nodes", [])
        if not isinstance(pending, list):
            raise ValueError("GLB scene.nodes must be node references")
        pending, reachable = list(pending), set()
        for root in pending:
            _glb_index(nodes, root, "scene node")
            if parents[root] is not None:
                raise ValueError("GLB scene must reference root nodes")
        while pending:
            index = pending.pop()
            reachable.add(index)
            pending.extend(nodes[index].get("children", []))
        scenes.append(reachable)
    bound_skins, joint_nodes = set(), set()
    for node_index, node in enumerate(nodes):
        if "skin" not in node:
            continue
        skin = _glb_index(skins, node["skin"], "skin")
        mesh = _glb_index(meshes, node.get("mesh"), "mesh")
        joints = skin.get("joints")
        if not isinstance(joints, list) or not joints or any(type(value) is not int for value in joints):
            raise ValueError("GLB skin.joints must be non-empty node references")
        if len(set(joints)) != len(joints):
            raise ValueError("GLB skin contains duplicate joints")
        for joint in joints:
            _glb_index(nodes, joint, "skin joint")
        common_ancestors = set.intersection(*(ancestors(joint) for joint in joints))
        if not common_ancestors:
            raise ValueError("GLB skin joints have no common root")
        if "skeleton" in skin:
            _glb_index(nodes, skin["skeleton"], "skin skeleton")
            if skin["skeleton"] not in common_ancestors:
                raise ValueError("GLB skin skeleton is not an ancestor of its joints")
        if not any(node_index in scene and set(joints) <= scene for scene in scenes):
            raise ValueError("GLB skinned mesh and joints must belong to the same scene")
        if "inverseBindMatrices" in skin:
            matrices, values = _glb_accessor(document, buffers, skin["inverseBindMatrices"])
            if matrices["type"] != "MAT4" or len(values) < len(joints):
                raise ValueError("GLB skin inverse bind matrices do not match joints")
            if any(tuple(row[index] for index in (3, 7, 11, 15)) != (0, 0, 0, 1) for row in values):
                raise ValueError("GLB inverse bind matrix fourth row is invalid")
        primitives = mesh.get("primitives")
        if not isinstance(primitives, list) or not primitives:
            raise ValueError("GLB skinned mesh has no primitives")
        for primitive in primitives:
            attributes = primitive.get("attributes", {})
            if not isinstance(attributes, dict) or not {"JOINTS_0", "WEIGHTS_0", "POSITION"} <= attributes.keys():
                raise ValueError("GLB skinned primitive is missing skin attributes")
            position, vertices = _glb_accessor(document, buffers, attributes["POSITION"])
            if position["type"] != "VEC3":
                raise ValueError("GLB skinned positions must use VEC3")
            if "indices" in primitive:
                index_entry, indices = _glb_accessor(document, buffers, primitive["indices"])
                if (index_entry["type"] != "SCALAR" or index_entry["componentType"] not in {5121, 5123, 5125}
                        or index_entry.get("normalized", False)):
                    raise ValueError("GLB mesh indices must be non-normalized unsigned scalars")
                restart = {5121: 255, 5123: 65535, 5125: 4294967295}[index_entry["componentType"]]
                if any(value >= len(vertices) or value == restart for (value,) in indices):
                    raise ValueError("GLB mesh index exceeds its available vertices or uses primitive restart")
            joint_sets = {key[7:] for key in attributes if re.fullmatch(r"JOINTS_[0-9]+", key)}
            weight_sets = {key[8:] for key in attributes if re.fullmatch(r"WEIGHTS_[0-9]+", key)}
            if joint_sets != weight_sets:
                raise ValueError("GLB skin joint and weight attribute sets do not match")
            sets = []
            for suffix in sorted(joint_sets, key=int):
                joint_entry, influences = _glb_accessor(document, buffers, attributes[f"JOINTS_{suffix}"])
                weight_entry, weights = _glb_accessor(document, buffers, attributes[f"WEIGHTS_{suffix}"], normalize=False)
                if (joint_entry["type"] != "VEC4" or joint_entry["componentType"] not in {5121, 5123}
                        or joint_entry.get("normalized", False) or weight_entry["type"] != "VEC4"
                        or weight_entry["componentType"] not in {5121, 5123, 5126}
                        or weight_entry["componentType"] != 5126 and not weight_entry.get("normalized", False)
                        or len(influences) != len(vertices) or len(weights) != len(vertices)):
                    raise ValueError("GLB skin accessor types or vertex counts do not match")
                sets.append((influences, weights, weight_entry["componentType"]))
            for vertex in range(len(vertices)):
                active, weight_values, quantized_sum = set(), [], 0
                float_weights = False
                for influences, weights, component_type in sets:
                    divisor = {5121: 255, 5123: 65535, 5126: 1}[component_type]
                    float_weights |= component_type == 5126
                    for joint, raw_weight in zip(influences[vertex], weights[vertex]):
                        weight = raw_weight / divisor
                        if not 0 <= joint < len(joints):
                            raise ValueError("GLB vertex joint index is outside skin.joints")
                        if weight < 0:
                            raise ValueError("GLB vertex skin weights must be non-negative")
                        if weight:
                            if joint in active:
                                raise ValueError("GLB vertex has duplicate non-zero joint influences")
                            active.add(joint)
                        weight_values.append(weight)
                        if component_type != 5126:
                            quantized_sum += raw_weight * (65535 // divisor)
                # The glTF specification documents this official validator threshold.
                if (not active or float_weights and abs(math.fsum(weight_values) - 1) > 2e-7 * len(active)
                        or not float_weights and quantized_sum != 65535):
                    raise ValueError("GLB vertex skin weights must sum to one")
        bound_skins.add(node["skin"])
        joint_nodes.update(joints)
    if not bound_skins:
        raise ValueError("GLB has no mesh bound to a skin")
    details = {"skins": len(bound_skins), "joints": len(joint_nodes), "rigValidated": True}
    if require_animation:
        animations = document.get("animations", [])
        if (type(minimum_animation_clips) is not int or minimum_animation_clips < 1
                or not isinstance(animations, list) or len(animations) < minimum_animation_clips):
            raise ValueError("GLB does not contain the required independent animation clips")
        animated_nodes = set().union(*(ancestors(joint) for joint in joint_nodes))
        clip_names = []
        for animation in animations:
            if not isinstance(animation, dict):
                raise ValueError("GLB animation must be an object")
            channels, samplers = animation.get("channels"), animation.get("samplers")
            if (not isinstance(channels, list) or not channels or not isinstance(samplers, list)
                    or not samplers or any(not isinstance(value, dict) for value in channels + samplers)):
                raise ValueError("GLB animation needs channels and samplers")
            targets, has_joint_channel = set(), False
            for channel in channels:
                sampler = _glb_index(samplers, channel.get("sampler"), "animation sampler")
                target = channel.get("target")
                if not isinstance(target, dict):
                    raise ValueError("GLB animation channel.target is invalid")
                target_node, target_path = target.get("node"), target.get("path")
                _glb_index(nodes, target_node, "animation target node")
                if target_path not in {"translation", "rotation", "scale", "weights"}:
                    raise ValueError("GLB animation target path is invalid")
                if (target_node, target_path) in targets:
                    raise ValueError("GLB animation has duplicate node/path channels")
                targets.add((target_node, target_path))
                input_entry, inputs = _glb_accessor(document, buffers, sampler.get("input"))
                output_entry, outputs = _glb_accessor(document, buffers, sampler.get("output"))
                if (input_entry["type"] != "SCALAR" or input_entry["componentType"] != 5126
                        or inputs[0][0] < 0 or any(left[0] >= right[0] for left, right in zip(inputs, inputs[1:]))):
                    raise ValueError("GLB animation timestamps must be bounded, non-negative and increasing")
                # glTF 3.6.2.5: FLOAT bounds in JSON are single-precision values.
                for field, actual in (("min", inputs[0][0]), ("max", inputs[-1][0])):
                    bound = input_entry.get(field)
                    if not isinstance(bound, list) or len(bound) != 1 or type(bound[0]) not in {int, float}:
                        raise ValueError("GLB animation timestamps bounds are invalid")
                    try:
                        rounded = struct.unpack("<f", struct.pack("<f", bound[0]))[0]
                    except (OverflowError, struct.error) as exc:
                        raise ValueError("GLB animation timestamps bounds are invalid") from exc
                    if rounded != actual:
                        raise ValueError("GLB animation timestamps bounds do not match binary values")
                interpolation = sampler.get("interpolation", "LINEAR")
                if interpolation not in {"LINEAR", "STEP", "CUBICSPLINE"}:
                    raise ValueError("GLB animation interpolation is unsupported")
                factor = 3 if interpolation == "CUBICSPLINE" else 1
                if factor == 3 and len(inputs) < 2:
                    raise ValueError("GLB cubic animation requires at least two keyframes")
                output_type = {"translation": "VEC3", "rotation": "VEC4", "scale": "VEC3", "weights": "SCALAR"}[target_path]
                if (output_entry["type"] != output_type
                        or output_entry["componentType"] != 5126 and (
                            target_path not in {"rotation", "weights"}
                            or output_entry["componentType"] not in {5120, 5121, 5122, 5123}
                            or not output_entry.get("normalized", False))):
                    raise ValueError("GLB animation output type does not match target")
                if target_path == "weights":
                    morph_mesh = _glb_index(meshes, nodes[target_node].get("mesh"), "morph animation mesh")
                    morph_counts = [len(value.get("targets", [])) for value in morph_mesh.get("primitives", [])]
                    if not morph_counts or not morph_counts[0] or len(set(morph_counts)) != 1:
                        raise ValueError("GLB weights animation requires matching morph targets")
                    factor *= morph_counts[0]
                if len(outputs) != len(inputs) * factor:
                    raise ValueError("GLB animation keyframe input/output counts do not match")
                if target_path == "rotation":
                    # Cubic tangent vectors are not rotations and need not be unit.
                    quaternions = outputs[1::3] if factor == 3 else outputs
                    if any(abs(math.sqrt(math.fsum(value * value for value in row)) - 1)
                           > GLTF_VALIDATOR_QUATERNION_TOLERANCE
                           for row in quaternions):
                        raise ValueError("GLB animation rotation keyframe quaternion is not a unit vector")
                if target_node in animated_nodes and target_path != "weights":
                    has_joint_channel = True
            if not has_joint_channel:
                raise ValueError("GLB animation has no skeleton animation channel")
            name = animation.get("name")
            if name is not None and not isinstance(name, str):
                raise ValueError("GLB animation name must be a string")
            clip_names.append(name)
        details.update(animationClips=clip_names, animationValidated=True)
    return details


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


def _validate_ply_payload(path, body_offset, ply_format, lines):
    """Check declared record presence, not mesh semantics. Author: yinjie."""
    sizes = {
        "char": 1, "uchar": 1, "int8": 1, "uint8": 1,
        "short": 2, "ushort": 2, "int16": 2, "uint16": 2,
        "int": 4, "uint": 4, "int32": 4, "uint32": 4,
        "float": 4, "float32": 4, "double": 8, "float64": 8,
    }
    elements = []
    for line in lines:
        fields = line.split()
        if not fields:
            continue
        if fields[0] == "element":
            try:
                count = int(fields[2]) if len(fields) == 3 else -1
            except ValueError as exc:
                raise ValueError("PLY element count is invalid") from exc
            if count < 0:
                raise ValueError("PLY element count is invalid")
            elements.append([count, 0, 0])
        elif fields[0] == "property":
            if not elements:
                raise ValueError("PLY property must follow an element")
            is_list = len(fields) == 5 and fields[1] == "list"
            if (not is_list and len(fields) != 3) or fields[1] == "list" and not is_list:
                raise ValueError("PLY property declaration is invalid")
            scalar_type = fields[2] if is_list else fields[1]
            if scalar_type not in sizes or is_list and fields[3] not in sizes:
                raise ValueError("PLY property type is unsupported")
            # A list may be empty, but its length field must still be present.
            elements[-1][1] += sizes[scalar_type]
            elements[-1][2] += 1
    if any(count and not properties for count, _, properties in elements):
        raise ValueError("PLY non-empty elements must declare properties")
    with path.open("rb") as file_obj:
        file_obj.seek(body_offset)
        if ply_format != "ascii":
            file_obj.seek(0, os.SEEK_END)
            minimum = sum(count * width for count, width, _ in elements)
            if file_obj.tell() - body_offset < minimum:
                raise ValueError("PLY body is truncated for its declared elements")
        else:
            for count, _, properties in elements:
                for _ in range(count):
                    row = file_obj.readline()
                    while row and not row.strip():
                        row = file_obj.readline()
                    if len(row.split()) < properties:
                        raise ValueError("PLY body is truncated for its declared elements")


def inspect_ply(path):
    with path.open("rb") as file_obj:
        header_bytes = file_obj.read(1024 * 1024)
    marker = re.search(rb"(?m)^end_header[ \t]*(?:\r?\n|$)", header_bytes)
    if marker is None:
        raise ValueError("PLY end_header was not found in the first MiB")
    header_slice = header_bytes[:marker.end()]
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
    _validate_ply_payload(path, marker.end(), parts[1], lines)
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


def inspect_fbx(path, *, require_rig=False, require_animation=False, minimum_animation_clips=1):
    configured = os.environ.get("LUX3D_BLENDER_EXECUTABLE")
    executable = str(pathlib.Path(configured).expanduser()) if configured else shutil.which("blender")
    if not executable or not pathlib.Path(executable).is_file():
        raise RuntimeError("FBX readback requires Blender; set LUX3D_BLENDER_EXECUTABLE or put blender on PATH")
    script = pathlib.Path(__file__).with_name("fbx_readback.py")
    with tempfile.TemporaryDirectory(prefix="lux3d-fbx-") as directory:
        report = pathlib.Path(directory) / "readback.json"
        try:
            process = subprocess.run(
                [executable, "--background", "--factory-startup", "--python-exit-code", "1",
                 "--python", str(script), "--", str(path), str(report)],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError("FBX readback did not finish within 60 seconds") from exc
        except OSError as exc:
            raise RuntimeError("Configured Blender could not be started for FBX readback") from exc
        if process.returncode or not report.is_file():
            raise ValueError("FBX cannot be read by the configured Blender importer")
        details = json.loads(report.read_text(encoding="utf-8"))
    if not details.get("meshes"):
        raise ValueError("FBX contains no readable model mesh")
    if require_rig and not details.get("rigValidated"):
        raise ValueError("FBX contains no mesh bound to a readable skeleton")
    if require_animation and (
        type(minimum_animation_clips) is not int or minimum_animation_clips < 1
        or len(details.get("animationClips", [])) < minimum_animation_clips
    ):
        raise ValueError("FBX does not contain the required independent skeleton animation clips")
    return details


def inspect_obj(path):
    """Validate standalone OBJ geometry without material or preview assumptions."""
    from lux3d_client import validate_retopology_download
    validate_retopology_download(str(path), "obj")
    vertices = faces = quads = 0
    with path.open(encoding="utf-8-sig") as stream:
        for line in stream:
            parts = line.split("#", 1)[0].split()
            if not parts:
                continue
            if parts[0] == "v":
                if len(parts) < 4 or not all(math.isfinite(float(v)) for v in parts[1:4]):
                    raise ValueError("Invalid OBJ vertex")
                vertices += 1
            elif parts[0] == "f":
                indices = [int(v.split("/")[0]) for v in parts[1:]]
                if len(indices) < 3 or any(i == 0 or abs(i) > vertices for i in indices):
                    raise ValueError("Invalid OBJ face")
                faces += 1
                quads += len(indices) == 4
    if not vertices or not faces:
        raise ValueError("OBJ has no geometry")
    return {"vertices": vertices, "faces": faces, "quads": quads}


def inspect_articulation_artifact(file_path, extension):
    if extension == ".zip" and not zipfile.is_zipfile(file_path):
        raise ValueError("Articulation ZIP is not a valid archive")
    return inspect_artifact(file_path, "glb" if extension == ".glb" else "file")


def inspect_result_file(path):
    """Validate a variable-format result without assuming a GLB-containing ZIP."""
    if path.suffix.lower() == ".zip" and not zipfile.is_zipfile(path):
        raise ValueError("Result ZIP is not a valid archive")
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            entries = [entry for entry in archive.infolist() if not entry.is_dir()]
            if not entries or any(not _safe_zip_name(entry.filename) for entry in entries):
                raise ValueError("Result archive is empty or contains unsafe paths")
            if archive.testzip():
                raise ValueError("Result archive failed CRC validation")
        return {"scope": "archive-integrity", "zipEntries": len(entries),
                "motionVerified": False}
    with path.open("rb") as stream:
        prefix = stream.read(512).lstrip().lower()
    if prefix.startswith((b"<!doctype html", b"<html", b"{", b"[", b"pk")):
        raise ValueError("Result is an error document or invalid archive")
    return {"scope": "nonempty-file-only", "motionVerified": False}


def inspect_artifact(file_path, format_hint=None, *, require_embedded_glb=False,
                     require_rig=False, require_animation=False, minimum_animation_clips=1):
    path, size = validate_path(file_path)
    output_format = format_hint or infer_format(path)
    if output_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported artifact format: {output_format}")
    if (require_rig or require_animation) and output_format not in {"glb", "fbx"}:
        raise ValueError("Rig and animation validation requires a GLB or bare FBX file")
    details = {}
    if output_format == "file":
        details = inspect_result_file(path)
    elif output_format == "glb":
        details = inspect_glb(path, size, require_embedded=require_embedded_glb,
                              require_rig=require_rig, require_animation=require_animation,
                              minimum_animation_clips=minimum_animation_clips)
    elif output_format == "fbx":
        details = inspect_fbx(path, require_rig=require_rig, require_animation=require_animation,
                              minimum_animation_clips=minimum_animation_clips)
    elif output_format in {"zip", "usdz", "obj_zip", "fbx_zip"}:
        details = inspect_zip(path, output_format)
    elif output_format == "obj":
        details = inspect_obj(path)
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
        "unity": ["glb", "fbx", "fbx_zip"],
        "unreal": ["fbx", "fbx_zip", "glb"],
        "blender": ["glb", "fbx", "fbx_zip", "obj_zip"],
        "dcc": ["glb", "fbx", "fbx_zip", "obj_zip"],
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


def validate_action_delivery(request, results, completion, artifacts, *, complete):
    """Check retained action facts against the accepted request and local files."""
    request_ids = request.get("animationIds")
    if (not isinstance(request_ids, list) or not request_ids
            or any(not isinstance(value, str) or not value.strip() for value in request_ids)
            or len(set(request_ids)) != len(request_ids)):
        raise ValueError("Retarget workflow must retain its requested animationIds")
    if not isinstance(results, list):
        raise ValueError("Retarget actionResults must be an array")
    successful, failed = set(), set()
    for result in results:
        if not isinstance(result, dict):
            raise ValueError("Retarget action result must be an object")
        action_id, status = result.get("animation_id"), result.get("status")
        if (not isinstance(action_id, str) or action_id not in request_ids
                or action_id in successful | failed or status not in {"success", "failed"}):
            raise ValueError("Retarget action result contradicts requested actions")
        (successful if status == "success" else failed).add(action_id)
        if status == "failed" and (
            not isinstance(result.get("error"), dict)
            or any(not isinstance(result["error"].get(key), str) or not result["error"][key] for key in ("code", "message"))
        ):
            raise ValueError("Failed retarget action must retain its error")
    delivered = set()
    for artifact in artifacts:
        action_ids = artifact.get("actionIds")
        if (not isinstance(action_ids, list) or not action_ids
                or any(not isinstance(value, str) or value not in successful for value in action_ids)
                or len(set(action_ids)) != len(action_ids) or delivered.intersection(action_ids)):
            raise ValueError("Retarget artifact actionIds must identify distinct successful actions")
        if request.get("animationOutputMode", "separate") == "separate" and len(action_ids) != 1:
            raise ValueError("Separate retarget files must each reference one action")
        delivered.update(action_ids)
    if complete and (
        successful | failed != set(request_ids) or delivered != successful
        or not isinstance(completion, dict)
        or completion.get("status") != ("partial" if failed else "complete")
        or completion.get("successfulActionIds") != [value for value in request_ids if value in successful]
        or completion.get("failedActionIds") != [value for value in request_ids if value in failed]
    ):
        raise ValueError("Retarget completion must match action results and delivered files")


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
        if artifact.get("format") == "file" and operation != "articulation-animation":
            raise ValueError("Generic file delivery is only supported for articulation")
        action_ids = artifact.get("actionIds")
        if action_ids is not None and (
            not isinstance(action_ids, list) or not action_ids
            or any(not isinstance(value, str) or not value.strip() or value != value.strip() for value in action_ids)
            or len(set(action_ids)) != len(action_ids)
        ):
            raise ValueError("Artifact actionIds must be distinct non-empty action identifiers")
        item = inspect_artifact(
            artifact["path"], artifact.get("format"),
            require_rig=operation in {"auto-rig", "animation-retarget"},
            require_animation=operation == "animation-retarget",
            minimum_animation_clips=len(action_ids) if action_ids else 1,
        )
        if action_ids is not None:
            item["actionIds"] = action_ids
        item["artifactId"] = artifact.get(
            "artifactId", f"{step_id}:{attempt_id}:{index + 1}"
        )
        item["sourceStepId"] = step_id
        item["version"] = artifact.get("version", attempt_id)
        inspected.append(item)
    formats = [item["format"] for item in inspected]
    manifest = {
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
    if operation == "animation-retarget" and ("actionResults" in spec or "completion" in spec):
        validate_action_delivery(spec.get("inputs", {}), spec.get("actionResults", []),
                                 spec.get("completion"), inspected, complete=True)
        manifest.update(actionResults=spec["actionResults"], completion=spec["completion"])
    return manifest


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
    inspect_parser.add_argument("--require-rig", action="store_true")
    inspect_parser.add_argument("--require-animation", action="store_true")
    inspect_parser.add_argument("--minimum-animation-clips", type=int, default=1)
    manifest = subparsers.add_parser("manifest")
    manifest.add_argument("--spec", required=True)
    manifest.add_argument("--output", required=True)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "inspect":
        result = inspect_artifact(args.file_path, args.format, require_rig=args.require_rig,
                                  require_animation=args.require_animation,
                                  minimum_animation_clips=args.minimum_animation_clips)
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
