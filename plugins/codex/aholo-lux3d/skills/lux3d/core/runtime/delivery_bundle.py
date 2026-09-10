"""Build portable multi-item delivery records from local workflow snapshots.

This module is offline: it never creates, queries or retries a cloud task.
"""

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import shutil
import sys

import artifact_delivery
import offline_preview
import task_metadata
import workflow_contracts


SPEC_SCHEMA = "lux3d.delivery-spec/v2"
MANIFEST_SCHEMA = "lux3d.delivery-bundle/v1"
STATE_SCHEMAS = {"lux3d.workflow-state/v1", "lux3d.workflow-state/v2"}
ID_PATTERN = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}\Z")
EXTENSIONS = {"obj_zip": "zip", "fbx_zip": "zip"}
RESERVED_IDS = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)
}
PRE_SUBMISSION_STATUSES = {
    "awaiting_submission_gate",
    "submitting",
    "submission_gate_passed_for_call",
    "submission_blocked",
    "submission_rejected",
    "submission_unknown",
}
with (
    pathlib.Path(__file__).resolve().parents[1] / "contracts" / "lux3d-workflow.v2.json"
).open(encoding="utf-8") as contract_file:
    STATE_STATUSES = set(json.load(contract_file)["task"]["runtimeStates"])
LEGACY_STATUSES = {"submitting", "awaiting_confirmation"}


def _identifier(value, field):
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        raise ValueError(
            f"{field} must be an ASCII letter/digit ID with optional - or _"
        )
    if value.upper() in RESERVED_IDS:
        raise ValueError(f"{field} is a reserved Windows filename")
    return value


def _object(value, allowed, field):
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    if set(value) - allowed:
        raise ValueError(f"{field} contains unsupported fields")


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return artifact_delivery.sanitize_error_message(value)


def _timestamp(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Local timestamp must be an ISO-8601 string")
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid local timestamp") from exc
    if parsed.utcoffset() is None:
        raise ValueError("Local timestamp must include a timezone")
    return parsed.isoformat()


def _validate_state(state):
    status = state.get("status")
    allowed_statuses = STATE_STATUSES | (
        LEGACY_STATUSES if state["schema"] == "lux3d.workflow-state/v1" else set()
    )
    if not isinstance(status, str) or status not in allowed_statuses:
        raise ValueError("Unsupported workflow status")
    if state.get("taskId") is None and status not in PRE_SUBMISSION_STATUSES:
        raise ValueError("Submitted workflow state requires taskId")
    provider = state.get("lastKnownProviderStatus")
    if provider is not None and (
        type(provider) is not int or provider not in {0, 1, 3, 4, 6}
    ):
        raise ValueError("Invalid provider status")
    expected_provider = {
        "succeeded": 3,
        "provider_succeeded": 3,
        "output_invalid": 3,
        "failed": 4,
        "cancelled": 6,
    }.get(status)
    if (
        expected_provider is not None
        and provider is not None
        and provider != expected_provider
    ):
        raise ValueError("Workflow status contradicts provider status")
    request = state.get("request")
    if (
        not isinstance(request, dict)
        or not isinstance(request.get("operation"), str)
        or request.get("operation") not in workflow_contracts.CREATE_PATHS
    ):
        raise ValueError("Unsupported workflow request operation")
    if not isinstance(request.get("region"), str) or request.get("region") not in {
        "cn",
        "international",
    }:
        raise ValueError("Task region must be cn or international")
    version = request.get("version")
    if request["operation"] not in {"four-view", "export"} and (
        not isinstance(version, str) or not version.strip()
    ):
        raise ValueError("Generation workflow version must be a non-empty string")
    if request["operation"] in {"four-view", "export"} and version is not None:
        raise ValueError("Four-view/export workflow does not accept version")
    expected = state.get("expectedFormats")
    if (
        not isinstance(expected, list)
        or any(
            not isinstance(value, str)
            or value not in artifact_delivery.SUPPORTED_FORMATS
            for value in expected
        )
        or len(set(expected)) != len(expected)
    ):
        raise ValueError("Invalid expectedFormats")
    if not expected and request["operation"] != "four-view":
        raise ValueError("3D workflow expectedFormats must not be empty")
    downloaded = state.get("downloadedArtifacts", [])
    if not isinstance(downloaded, list) or any(
        not isinstance(value, dict)
        or not isinstance(value.get("path"), str)
        or value.get("format") not in expected
        for value in downloaded
    ):
        raise ValueError("Invalid downloadedArtifacts")
    if status == "succeeded" and set(expected) != {
        value["format"] for value in downloaded
    }:
        raise ValueError("Succeeded workflow is missing requested artifacts")


def _local_timing(state):
    started = _timestamp(state.get("createdAt"))
    completed = _timestamp(state.get("localCompletedAt"))
    duration = None
    if completed is not None:
        if started is None or state["status"] != "succeeded":
            raise ValueError("Local completion requires a started, successful workflow")
        elapsed = (
            datetime.datetime.fromisoformat(completed)
            - datetime.datetime.fromisoformat(started)
        )
        if elapsed < datetime.timedelta(0):
            raise ValueError("Local completion cannot precede workflow start")
        duration = elapsed // datetime.timedelta(milliseconds=1)
    return {
        "localStartedAt": started,
        "localUpdatedAt": _timestamp(state.get("updatedAt")),
        "localCompletedAt": completed,
        "localDurationMs": duration,
    }


def _read_state(value, spec_dir):
    path = pathlib.Path(_text(value, "statePath"))
    if not path.is_absolute():
        path = spec_dir / path
    with path.open("r", encoding="utf-8-sig") as file_obj:
        state = json.load(file_obj)
    if (
        not isinstance(state, dict)
        or not isinstance(state.get("schema"), str)
        or state["schema"] not in STATE_SCHEMAS
    ):
        raise ValueError("Unsupported workflow state schema")
    artifact_delivery.assert_no_secrets(state)
    _validate_state(state)
    return state, path.resolve().parent


def _task(state):
    task_id = state.get("taskId")
    if task_id is None:
        return None
    task_id = task_metadata.normalize_task_id(task_id)
    request = state["request"]
    region = request["region"]
    metadata = state.get("taskMetadata")
    created = (
        task_metadata.created_at(metadata, task_id, region)
        if metadata is not None
        else None
    )
    return {
        "id": f"{region}:{task_id}",
        "taskId": task_id,
        "region": region,
        "operation": request.get("operation"),
        "version": request.get("version"),
        "providerStatus": state.get("lastKnownProviderStatus"),
        # Only the verified task-list field supplies creation time. Local timestamps
        # and lastModified never establish provider duration or settled charges.
        "createdAt": created,
        "creationSources": [metadata] if metadata is not None else [],
        "durationMs": None,
        "actualCredits": {"status": "unavailable", "value": None, "source": None},
    }


def _merge_task(previous, current):
    fact_keys = set(previous) - {"createdAt", "creationSources"}
    if any(previous[key] != current[key] for key in fact_keys) or (
        previous["createdAt"] is not None
        and current["createdAt"] is not None
        and previous["createdAt"] != current["createdAt"]
    ):
        raise ValueError(f"Conflicting snapshots for task: {current['id']}")
    merged = dict(previous)
    merged["createdAt"] = (
        previous["createdAt"]
        if previous["createdAt"] is not None
        else current["createdAt"]
    )
    merged["creationSources"] = list(previous["creationSources"])
    for source in current["creationSources"]:
        if source not in merged["creationSources"]:
            merged["creationSources"].append(source)
    return merged


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON keys are not allowed in scene evidence")
        result[key] = value
    return result


def _execution_reference(value, field):
    # Evidence is copied byte-for-byte: reject URL/credential/path-bearing
    # references instead of redacting only the manifest and leaking the original.
    if (
        not isinstance(value, str)
        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9:._/-]{0,511}", value)
        or "://" in value
        or re.match(r"^[A-Za-z]:/", value)
    ):
        raise ValueError(
            f"{field} must be an opaque tool/session reference, not a URL or path"
        )
    return value


def _ready_scene(scene, spec_dir, items, artifacts, sources):
    export_path = spec_dir / _text(scene.get("artifactPath"), "scene.artifactPath")
    evidence_path = spec_dir / _text(scene.get("evidencePath"), "scene.evidencePath")
    inspected = artifact_delivery.inspect_artifact(
        export_path, "glb", require_embedded_glb=True
    )
    if any(
        inspected["validation"].get(key, 0) <= 0
        for key in ("scenes", "nodes", "meshes")
    ):
        raise ValueError("Scene export must contain a scene, nodes and a mesh")
    evidence_bytes = evidence_path.read_bytes()
    evidence = json.loads(
        evidence_bytes.decode("utf-8-sig"), object_pairs_hook=_unique_json_object
    )
    _object(
        evidence,
        {
            "schema",
            "kind",
            "toolName",
            "callId",
            "recordRef",
            "executedAt",
            "exportSha256",
            "sources",
        },
        "scene evidence",
    )
    artifact_delivery.assert_no_secrets(evidence)
    if evidence.get("schema") != "lux3d.scene-execution/v1":
        raise ValueError("Unsupported scene evidence schema")
    kind = _text(evidence.get("kind"), "scene evidence kind")
    if kind not in {"external-tool", "development-fixture"}:
        raise ValueError("Unsupported scene evidence kind")
    if evidence.get("exportSha256") != inspected["sha256"]:
        raise ValueError("Scene export digest does not match its execution evidence")
    execution = {
        "kind": kind,
        "toolName": _execution_reference(evidence.get("toolName"), "scene toolName"),
        "callId": _execution_reference(evidence.get("callId"), "scene callId"),
        "recordRef": _execution_reference(evidence.get("recordRef"), "scene recordRef"),
        "executedAt": _timestamp(_text(evidence.get("executedAt"), "scene executedAt")),
        # A supplied record is provenance, not proof that this process saw the tool run.
        "verification": "supplied-record-not-independently-verified",
    }
    bindings = evidence.get("sources")
    if not isinstance(bindings, list) or not bindings:
        raise ValueError("Scene evidence must reference its source artifacts")
    normalized, seen = [], set()
    for binding in bindings:
        _object(
            binding, {"itemId", "attemptId", "artifactId", "sha256"}, "scene source"
        )
        item_id = _identifier(binding.get("itemId"), "scene itemId")
        attempt_id = _identifier(binding.get("attemptId"), "scene attemptId")
        artifact_id = _text(binding.get("artifactId"), "scene artifactId")
        item, artifact = items.get(item_id), artifacts.get(artifact_id)
        if (
            item is None
            or item["selectedAttemptId"] != attempt_id
            or artifact_id not in item["artifactIds"]
            or artifact is None
            or artifact["attemptId"] != attempt_id
        ):
            raise ValueError(
                "Scene source must match an item's selected attempt and artifact"
            )
        if binding.get("sha256") != artifact["sha256"]:
            raise ValueError(
                "Scene source digest does not match the delivered artifact"
            )
        identity = (item_id, artifact_id)
        if identity in seen:
            raise ValueError("Duplicate scene source binding")
        seen.add(identity)
        normalized.append(
            {
                "itemId": item_id,
                "attemptId": attempt_id,
                "artifactId": artifact_id,
                "sha256": artifact["sha256"],
            }
        )
    # Two separators keep these IDs disjoint from every attempt:format asset ID.
    scene_id, evidence_id = "scene:assembled:glb", "scene:execution:json"
    artifacts[scene_id] = {
        **inspected,
        "id": scene_id,
        "role": "assembled-scene",
        "attemptId": None,
        "taskRef": None,
        "path": "scene/scene.glb",
    }
    artifacts[evidence_id] = {
        "id": evidence_id,
        "role": "scene-execution-evidence",
        "format": "json",
        "attemptId": None,
        "taskRef": None,
        "path": "evidence/scene-execution.json",
        "size": len(evidence_bytes),
        "sha256": hashlib.sha256(evidence_bytes).hexdigest(),
        "validation": {"valid": True, "schema": evidence["schema"]},
    }
    sources[scene_id], sources[evidence_id] = export_path, evidence_path
    return {
        "status": "ready",
        "artifactId": scene_id,
        "evidenceArtifactId": evidence_id,
        "sources": normalized,
        "execution": execution,
    }


def _scene(spec, spec_dir, items, artifacts, sources):
    scene = spec.get("scene", {"status": "not-requested"})
    if not isinstance(scene, dict) or not isinstance(scene.get("status"), str):
        raise ValueError("scene must be an object")
    if scene.get("status") == "not-requested" and set(scene) == {"status"}:
        return {"status": "not-requested"}
    if scene.get("status") == "ready" and set(scene) == {
        "status",
        "artifactPath",
        "evidencePath",
    }:
        try:
            return _ready_scene(scene, spec_dir, items, artifacts, sources)
        except (OSError, ValueError):
            # Scene validation is a separate outcome, not a new generation or
            # permission to discard independently validated item artifacts.
            return {
                "status": "failed",
                "failureCode": "scene-validation-failed",
                "reason": "Scene export or execution evidence could not be validated. Independent items are preserved.",
            }
    if scene.get("status") in {"unavailable", "failed", "pending"} and set(scene) == {
        "status",
        "reason",
    }:
        return {
            "status": scene["status"],
            "reason": _text(scene.get("reason"), "scene.reason"),
        }
    raise ValueError(
        "Invalid scene result; a ready scene requires a validated export and tool evidence"
    )


def _prepare(spec, spec_dir):
    if not isinstance(spec, dict) or spec.get("schema") != SPEC_SCHEMA:
        raise ValueError(f"Delivery spec schema must be {SPEC_SCHEMA}")
    artifact_delivery.assert_no_secrets(spec)
    _object(spec, {"schema", "title", "items", "scene"}, "Delivery spec")
    spec_dir = pathlib.Path(spec_dir).resolve()
    title = _text(spec.get("title"), "title")
    source_items = spec.get("items")
    if not isinstance(source_items, list) or not source_items:
        raise ValueError("items must be a non-empty list")
    items, attempts, tasks, artifacts, sources = {}, {}, {}, {}, {}
    snapshots = {}
    portable_ids = {}
    for item in source_items:
        _object(item, {"id", "label", "attempts", "selectedAttemptId"}, "item")
        item_id = _identifier(item.get("id"), "item.id")
        if item_id in items:
            raise ValueError(f"Duplicate item ID: {item_id}")
        refs = item.get("attempts")
        if not isinstance(refs, list) or not refs:
            raise ValueError("Each item must explicitly reference its attempts")
        attempt_ids = []
        for ref in refs:
            _object(ref, {"id", "statePath"}, "attempt reference")
            attempt_id = _identifier(ref.get("id"), "attempt.id")
            previous_id = portable_ids.setdefault(attempt_id.casefold(), attempt_id)
            if previous_id != attempt_id:
                raise ValueError("Attempt IDs collide on a case-insensitive filesystem")
            state, state_dir = _read_state(ref.get("statePath"), spec_dir)
            snapshot = (state, state_dir)
            if attempt_id in snapshots and snapshots[attempt_id] != snapshot:
                raise ValueError(f"Conflicting snapshots for attempt: {attempt_id}")
            if attempt_id not in attempts:
                snapshots[attempt_id] = snapshot
                task = _task(state)
                if task is not None:
                    task_ref = task["id"]
                    tasks[task_ref] = (
                        _merge_task(tasks[task_ref], task)
                        if task_ref in tasks
                        else task
                    )
                else:
                    task_ref = None
                artifact_ids = []
                for source in state.get("downloadedArtifacts") or []:
                    path = pathlib.Path(source["path"])
                    if not path.is_absolute():
                        path = state_dir / path
                    inspected = artifact_delivery.inspect_artifact(
                        path, source.get("format")
                    )
                    output_format = inspected["format"]
                    artifact_id = f"{attempt_id}:{output_format}"
                    if artifact_id in artifacts:
                        raise ValueError(
                            f"Duplicate artifact format in attempt: {attempt_id}"
                        )
                    extension = EXTENSIONS.get(output_format, output_format)
                    sources[artifact_id] = pathlib.Path(inspected["path"])
                    artifacts[artifact_id] = {
                        **inspected,
                        "id": artifact_id,
                        "attemptId": attempt_id,
                        "taskRef": task_ref,
                        "path": f"assets/{attempt_id}/{output_format}.{extension}",
                    }
                    artifact_ids.append(artifact_id)
                attempts[attempt_id] = {
                    "id": attempt_id,
                    "taskRef": task_ref,
                    "status": state.get("status"),
                    **_local_timing(state),
                    "artifactIds": artifact_ids,
                }
            if attempt_id in attempt_ids:
                raise ValueError(f"Duplicate attempt reference in item: {attempt_id}")
            attempt_ids.append(attempt_id)
        selected_id = item.get("selectedAttemptId")
        if selected_id is not None:
            _identifier(selected_id, "selectedAttemptId")
        if selected_id is not None and selected_id not in attempt_ids:
            raise ValueError(
                "selectedAttemptId must reference one of the item's attempts"
            )
        selected = attempts.get(selected_id)
        item_artifacts = list(selected["artifactIds"]) if selected else []
        selected_task = tasks.get(selected["taskRef"]) if selected else None
        completed = (
            selected is not None
            and selected["status"] == "succeeded"
            and bool(item_artifacts)
            and selected_task is not None
            and selected_task["providerStatus"] == 3
        )
        items[item_id] = {
            "id": item_id,
            "label": _text(item.get("label"), "item.label"),
            "attemptIds": attempt_ids,
            "selectedAttemptId": selected_id,
            "artifactIds": item_artifacts,
            "status": "complete" if completed else "incomplete",
        }
    scene = _scene(spec, spec_dir, items, artifacts, sources)
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "createdAt": artifact_delivery.utc_now(),
        "title": title,
        # Asset preparation is not the full delivery: the offline preview and
        # verified service metadata still have their own completion gates.
        "status": "incomplete",
        "assetStatus": "complete"
        if all(item["status"] == "complete" for item in items.values())
        else "incomplete",
        "preview": {"status": "not-built", "path": None},
        "items": list(items.values()),
        "attempts": list(attempts.values()),
        "tasks": list(tasks.values()),
        "artifacts": list(artifacts.values()),
        "credits": {"status": "incomplete", "total": None},
        "scene": scene,
    }
    return manifest, sources


def build_manifest(spec, spec_dir):
    """Validate snapshots/assets and return a URL-free portable delivery record."""
    return _prepare(spec, spec_dir)[0]


def prepare_bundle(spec_path, output_dir, *, locale="en"):
    """Copy verified originals into a new directory; publish the manifest last.

    An existing destination is never reused or removed. On an I/O failure the
    new directory may retain partial files, but has no completion manifest.
    """
    if locale not in offline_preview.SUPPORTED_LOCALES:
        raise ValueError("Unsupported preview locale; choose en or zh-CN")
    spec_path = pathlib.Path(spec_path).resolve()
    with spec_path.open("r", encoding="utf-8-sig") as file_obj:
        spec = json.load(file_obj)
    manifest, sources = _prepare(spec, spec_path.parent)
    target = pathlib.Path(output_dir).absolute()
    # Refuse link traversal on the destination, including a dangling final link.
    for component in (target, *target.parents):
        if component.is_symlink():
            raise ValueError("Delivery destination must not traverse symlinks")
    try:
        target.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise FileExistsError(
            "Delivery directory already exists; choose a new output directory"
        ) from exc
    for artifact in manifest["artifacts"]:
        destination = target / artifact["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        with (
            sources[artifact["id"]].open("rb") as source,
            destination.open("xb") as copied,
        ):
            shutil.copyfileobj(source, copied)
        if artifact_delivery.sha256_file(destination) != artifact["sha256"]:
            raise ValueError(
                "Source artifact changed while copying; no delivery manifest was published"
            )
    offline_preview.write_preview(target, manifest, locale)
    artifact_delivery.write_json_atomic(target / "lux3d-delivery.json", manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Prepare an offline multi-item Lux3D delivery."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser(
        "prepare",
        help="Copy source assets and write offline HTML plus a manifest (no cloud calls).",
    )
    prepare.add_argument("--spec", required=True)
    prepare.add_argument("--output-dir", required=True)
    prepare.add_argument(
        "--locale", choices=offline_preview.SUPPORTED_LOCALES, default="en",
        help="Offline page language, explicitly selected by the host (default: en).",
    )
    args = parser.parse_args()
    result = prepare_bundle(args.spec, args.output_dir, locale=args.locale)
    print(
        json.dumps(
            {
                "manifest": str(
                    pathlib.Path(args.output_dir).absolute() / "lux3d-delivery.json"
                ),
                "status": result["status"],
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(
            f"[ERROR] {artifact_delivery.sanitize_error_message(exc)}", file=sys.stderr
        )
        raise SystemExit(1)
