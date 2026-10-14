"""Run resumable Lux3D workflows and produce verified delivery manifests."""

import argparse
import datetime
import json
import os
import pathlib
import re
import sys

import artifact_delivery
import lux3d_client
import workflow_contracts


STATE_SCHEMA = "lux3d.workflow-state/v2"
LEGACY_STATE_SCHEMA = "lux3d.workflow-state/v1"
DELIVERY_FILENAME = "lux3d-delivery.json"
OPERATIONS = {
    "articulation-animation",
    "image-to-3d",
    "text-to-3d",
    "material-transfer",
    "four-view",
    "mesh-retopology",
    "export",
    "auto-rig",
    "animation-retarget",
}
PREVIEW_OPERATIONS = {"four-view"}
ARTIFACT_OPERATIONS = OPERATIONS - PREVIEW_OPERATIONS
COMMON_FIELDS = {
    "operation",
    "region",
    "version",
    "outputBasename",
    "target",
    "submission",
}
OPERATION_FIELDS = {
    "articulation-animation": {"glbUrl", "prompt"},
    "image-to-3d": {
        "img",
        "imgs",
        "faceCount",
        "outputFormat",
        "enablePbr",
        "aiPredictSize",
        "customSize",
    },
    "text-to-3d": {
        "prompt",
        "style",
        "img",
        "faceCount",
        "outputFormat",
        "enablePbr",
        "aiPredictSize",
        "customSize",
    },
    "material-transfer": {
        "img",
        "meshUrl",
        "outputFormat",
        "aiPredictSize",
        "customSize",
    },
    "four-view": {"img", "prompt"},
    "mesh-retopology": {"modelUrl", "faceLimit", "quad", "bakeTextures", "textureSize"},
    "export": {"modelUrl", "outputFormat"},
    "auto-rig": {"modelUrl"},
    "animation-retarget": {"rigModelUrl", "animationIds", "animationOutputMode", "outFormat", "animateInPlace"},
}
DEFAULT_BASENAMES = {
    "articulation-animation": "lux3d-articulation",
    "image-to-3d": "lux3d-image-model",
    "text-to-3d": "lux3d-text-model",
    "material-transfer": "lux3d-material-model",
    "four-view": "lux3d-four-view",
    "mesh-retopology": "lux3d-retopology",
    "export": "lux3d-export",
    "auto-rig": "lux3d-rigged-character",
    "animation-retarget": "lux3d-animated-character",
}
QUERYABLE_STATES = {
    "submitted",
    "running",
    "query_error",
    "output_invalid",
    "provider_succeeded",
    "delivery_failed",
}


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")


def read_json(path):
    source = pathlib.Path(path).expanduser().resolve()
    with source.open("r", encoding="utf-8") as file_obj:
        payload = json.load(file_obj)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {source}")
    return payload


def update_state(state_path, state, **changes):
    state.update(changes)
    if "lastError" in state:
        state["lastError"] = artifact_delivery.sanitize_error_message(state["lastError"])
    state["updatedAt"] = utc_now()
    if changes.get("status") == "succeeded" and state.get("localCompletedAt") is None:
        state["localCompletedAt"] = state["updatedAt"]
    persisted = artifact_delivery.without_transient_urls(state)
    artifact_delivery.assert_no_secrets(persisted)
    artifact_delivery.write_json_atomic(state_path, persisted)
    state.clear()
    state.update(persisted)


def create_state_exclusive(state_path, state):
    """Atomically reserve one local workflow state path before any POST."""
    target = pathlib.Path(state_path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    state["updatedAt"] = utc_now()
    persisted = artifact_delivery.without_transient_urls(state)
    artifact_delivery.assert_no_secrets(persisted)
    try:
        with target.open("x", encoding="utf-8") as file_obj:
            json.dump(persisted, file_obj, ensure_ascii=False, indent=2)
            file_obj.write("\n")
            file_obj.flush()
            os.fsync(file_obj.fileno())
    except FileExistsError as exc:
        raise FileExistsError(
            "State file already exists; use resume instead of creating "
            f"another task: {target}"
        ) from exc
    state.clear()
    state.update(persisted)


def migrate_legacy_state(state_path, state):
    if state.get("schema") != LEGACY_STATE_SCHEMA:
        return state
    request = state.get("request") or {}
    region = lux3d_client.normalize_region(request.get("region"))
    state["schema"] = STATE_SCHEMA
    state.setdefault("accountRef", "legacy-account-unavailable")
    state.setdefault("environmentRef", f"lux3d:{region}")
    state.setdefault("stage", "execution")
    state.setdefault(
        "commerce",
        {
            "legacyState": True,
            "accountRef": state["accountRef"],
            "stepId": "legacy-step",
            "attemptId": "legacy-attempt",
            "requestKey": "legacy-request-unavailable",
            "retryCount": 0,
        },
    )
    state.setdefault(
        "submissionCheck",
        {"legacyState": True, "reusable": False},
    )
    update_state(state_path, state)
    return state


def validate_generation_port_context(generation_port, state):
    if generation_port is None:
        raise ValueError(
            "A GenerationPort matching the persisted account and environment is required"
        )
    try:
        context = generation_port.context()
    except Exception as exc:
        raise RuntimeError("GenerationPort context lookup failed") from exc
    if not isinstance(context, dict):
        raise ValueError("GenerationPort context must be an object")
    expected_environment = state.get("environmentRef")
    if context.get("environmentRef") != expected_environment:
        raise ValueError("GenerationPort environment does not match workflow state")
    expected_account = state.get("accountRef")
    if (
        expected_account != "legacy-account-unavailable"
        and context.get("accountRef") != expected_account
    ):
        raise ValueError("GenerationPort account does not match workflow state")
    return context


def finalize_submission_registry(
    submission_registry, intent, *, outcome, task_id=None
):
    try:
        submission_registry.finalize(
            intent, outcome=outcome, task_id=task_id
        )
        return "ok"
    except Exception:
        return "error"


def validate_basename(value, operation):
    basename = str(value or DEFAULT_BASENAMES[operation]).strip()
    if not basename or basename in {".", ".."}:
        raise ValueError("outputBasename must be a non-empty filename stem")
    if len(basename) > 120:
        raise ValueError("outputBasename must not exceed 120 characters")
    if pathlib.PurePath(basename).name != basename or re.search(r'[<>:"/\\|?*\x00-\x1f]', basename):
        raise ValueError("outputBasename must not contain path separators or reserved characters")
    return basename


def validate_target(target, operation):
    if operation in PREVIEW_OPERATIONS and target is None:
        return None
    if not isinstance(target, dict) or not str(target.get("kind") or "").strip():
        raise ValueError("target.kind is required for workflows that deliver 3D artifacts")
    artifact_delivery.assert_no_secrets(target, "$.target")
    return target


def _validate_image_request(request, region):
    img = request.get("img")
    imgs = request.get("imgs")
    if (img is None) == (imgs is None):
        raise ValueError("image-to-3d requires exactly one of img or imgs")
    if img is not None:
        request["img"] = lux3d_client.validate_http_url(img, "img", region)
    else:
        if not isinstance(imgs, list) or not 1 <= len(imgs) <= 32:
            raise ValueError("imgs must be an ordered list of 1-32 image URLs")
        request["imgs"] = [
            lux3d_client.validate_http_url(item, f"imgs[{index}]", region)
            for index, item in enumerate(imgs)
        ]
    version = request.get("version")
    request["version"] = lux3d_client.validate_version(version)
    formats = lux3d_client.validate_generation_options(
        version,
        request.get("outputFormat"),
        request.get("enablePbr"),
        request.get("customSize"),
    )
    if request.get("outputFormat") is not None:
        request["outputFormat"] = formats
    if request.get("faceCount") is not None:
        request["faceCount"] = lux3d_client.validate_face_count(
            request["faceCount"]
        )
    if request.get("aiPredictSize") is not None:
        request["aiPredictSize"] = lux3d_client.validate_boolean(
            request["aiPredictSize"], "aiPredictSize"
        )
    if request.get("customSize") is not None:
        request["customSize"] = lux3d_client.validate_custom_size(
            request["customSize"]
        )


def _validate_text_request(request, region):
    request["prompt"] = lux3d_client.validate_prompt(request.get("prompt"))
    request["version"] = lux3d_client.validate_version(request.get("version"))
    if request.get("style") is not None:
        request["style"] = lux3d_client.validate_style(request["style"])
    if request.get("img") is not None:
        request["img"] = lux3d_client.validate_http_url(
            request["img"], "img", region
        )
    version = request.get("version")
    formats = lux3d_client.validate_generation_options(
        version,
        request.get("outputFormat"),
        request.get("enablePbr"),
        request.get("customSize"),
    )
    if request.get("outputFormat") is not None:
        request["outputFormat"] = formats
    if request.get("faceCount") is not None:
        request["faceCount"] = lux3d_client.validate_face_count(
            request["faceCount"]
        )
    if request.get("aiPredictSize") is not None:
        request["aiPredictSize"] = lux3d_client.validate_boolean(
            request["aiPredictSize"], "aiPredictSize"
        )
    if request.get("customSize") is not None:
        request["customSize"] = lux3d_client.validate_custom_size(
            request["customSize"]
        )


def _validate_material_request(request, region):
    request["img"] = lux3d_client.validate_http_url(
        request.get("img"), "img", region
    )
    request["meshUrl"] = lux3d_client.validate_url_suffix(
        request.get("meshUrl"), "meshUrl", (".glb",), region
    )
    request["version"] = lux3d_client.validate_material_version(
        request.get("version")
    )
    formats = lux3d_client.validate_material_options(
        request.get("version"),
        request.get("outputFormat"),
        request.get("aiPredictSize"),
        request.get("customSize"),
    )
    if request.get("outputFormat") is not None:
        request["outputFormat"] = formats
    if request.get("aiPredictSize") is not None:
        request["aiPredictSize"] = lux3d_client.validate_boolean(
            request["aiPredictSize"], "aiPredictSize"
        )
    if request.get("customSize") is not None:
        request["customSize"] = lux3d_client.validate_custom_size(
            request["customSize"]
        )


def prepare_request(request):
    artifact_delivery.assert_no_secrets(request)
    operation = request.get("operation")
    if operation not in OPERATIONS:
        raise ValueError(
            "operation must be image-to-3d, text-to-3d, material-transfer, "
            "four-view, mesh-retopology, export, articulation-animation, auto-rig, or animation-retarget"
        )
    unknown = set(request) - COMMON_FIELDS - OPERATION_FIELDS[operation]
    if unknown:
        raise ValueError("Unsupported request fields for %s: %s" % (operation, ", ".join(sorted(unknown))))
    region = lux3d_client.normalize_region(request.get("region"))
    request["region"] = region
    request["outputBasename"] = validate_basename(request.get("outputBasename"), operation)
    validate_target(request.get("target"), operation)

    if operation == "image-to-3d":
        _validate_image_request(request, region)
    elif operation == "text-to-3d":
        _validate_text_request(request, region)
    elif operation == "material-transfer":
        _validate_material_request(request, region)
    elif operation == "animation-retarget":
        request.update(lux3d_client.build_animation_retarget_payload(request.get("rigModelUrl"), request.get("animationIds"), animationOutputMode=request.get("animationOutputMode"), outFormat=request.get("outFormat"), animateInPlace=request.get("animateInPlace"), region=region))
    elif operation == "auto-rig":
        request.update(lux3d_client.build_auto_rig_payload(request.get("modelUrl"), region=region))
    elif operation == "articulation-animation":
        if "version" in request:
            raise ValueError("articulation-animation does not accept version")
        request.update(lux3d_client.build_articulation_animation_payload(
            request.get("glbUrl"), request.get("prompt"), region=region,
        ))
    elif operation == "mesh-retopology":
        if request.get("version") is not None:
            raise ValueError("mesh-retopology does not accept version")
        request.update(lux3d_client.build_mesh_retopology_payload(
            request.get("modelUrl"), request.get("faceLimit"),
            quad=request.get("quad", True),
            bakeTextures=request.get("bakeTextures", False),
            textureSize=request.get("textureSize", 2048), region=region,
        ))
    elif operation in PREVIEW_OPERATIONS:
        payload = lux3d_client.build_multimodal_payload(
            request.get("img"), request.get("prompt"), region
        )
        request.update(payload)
    else:
        model_url, formats = lux3d_client.validate_export_options(
            request.get("modelUrl"), request.get("outputFormat"), region
        )
        request["modelUrl"] = model_url
        if request.get("outputFormat") is not None:
            request["outputFormat"] = formats
    if operation in {"auto-rig", "animation-retarget", "four-view", "export"} and request.get("version") is not None:
        raise ValueError(f"{operation} does not accept version")
    return request


def validate_request(request):
    request = prepare_request(request)
    workflow_contracts.validate_submission_context(request)
    return request


def validate_persisted_request(request):
    """Validate the URL-free request context required to resume by task id."""
    if not isinstance(request, dict):
        raise ValueError("Workflow state request must be an object")
    if artifact_delivery.without_transient_urls(request) != request:
        raise ValueError("Workflow state request must not contain temporary URL fields")
    operation = request.get("operation")
    if operation not in OPERATIONS:
        raise ValueError("Workflow state has an unsupported operation")
    request["region"] = lux3d_client.normalize_region(request.get("region"))
    request["outputBasename"] = validate_basename(
        request.get("outputBasename"), operation
    )
    validate_target(request.get("target"), operation)
    return request


def expected_formats(request):
    operation = request["operation"]
    if operation in {"image-to-3d", "text-to-3d"}:
        return lux3d_client.generation_result_formats(
            request["version"], request.get("outputFormat")
        )
    if operation == "mesh-retopology":
        return ["glb", "obj"]
    if operation == "material-transfer":
        return lux3d_client.material_result_formats(request.get("outputFormat"))
    if operation == "export":
        return lux3d_client.export_result_formats(
            request["modelUrl"], request.get("outputFormat")
        )
    if operation == "auto-rig":
        return ["glb"]
    if operation == "animation-retarget":
        return [request["outFormat"]]
    return []


def fixed_output_slots(request):
    """Return a fixed provider slot contract for operations that define one."""
    if request["operation"] == "articulation-animation":
        return lux3d_client.ARTICULATION_OUTPUT_SLOTS
    if request["operation"] == "mesh-retopology":
        return lux3d_client.RETOPOLOGY_OUTPUT_SLOTS
    if request["operation"] == "material-transfer":
        return lux3d_client.MATERIAL_OUTPUT_SLOTS
    if request["operation"] == "export":
        return lux3d_client.EXPORT_OUTPUT_SLOTS
    return None


def validate_requested_provider_outputs(request, outputs, formats):
    """Ensure image/text success contains every artifact requested this run."""
    if request["operation"] == "animation-retarget":
        try:
            actions = lux3d_client.validate_animation_results(outputs, request["animationIds"], outFormat=request.get("outFormat", "glb"), animationOutputMode=request.get("animationOutputMode", "separate"))
            if not any(action["status"] == "success" for action in actions):
                raise ValueError("Provider status 3 has no successful animation result")
            return actions
        except ValueError as exc:
            raise lux3d_client.TaskOutputError(f"Animation result does not match the accepted request: {exc}") from exc
    if request["operation"] == "articulation-animation":
        try:
            lux3d_client.validate_http_url(outputs, "articulation result")
        except ValueError as exc:
            raise lux3d_client.TaskOutputError("Articulation requires one result URL") from exc
        return
    if request["operation"] == "mesh-retopology":
        if not isinstance(outputs, dict) or not {"glb", "obj"} <= outputs.keys():
            raise lux3d_client.TaskOutputError("Retopology requires GLB and OBJ")
        try:
            for name, url in outputs.items():
                if name not in lux3d_client.RETOPOLOGY_OUTPUT_SLOTS:
                    raise ValueError("Unknown retopology artifact")
                lux3d_client.validate_http_url(url, name)
        except ValueError as exc:
            raise lux3d_client.TaskOutputError("Invalid retopology output") from exc
        return
    if request["operation"] not in {"image-to-3d", "text-to-3d"}:
        return
    try:
        lux3d_client.map_artifact_urls(outputs, formats)
    except ValueError as exc:
        raise lux3d_client.TaskOutputError(
            f"Task succeeded but requested outputs are incomplete: {exc}"
        ) from exc


def submit_task(request):
    operation = request["operation"]
    region = request["region"]
    content_id = request.get("contentId")
    if operation == "animation-retarget":
        return lux3d_client.create_animation_retarget_task(request["rigModelUrl"], request["animationIds"], animationOutputMode=request.get("animationOutputMode"), outFormat=request.get("outFormat"), animateInPlace=request.get("animateInPlace"), region=region, content_id=content_id)
    if operation == "auto-rig":
        return lux3d_client.create_auto_rig_task(request["modelUrl"], region=region, content_id=content_id)
    if operation == "articulation-animation":
        return lux3d_client.create_articulation_animation_task(
            request["glbUrl"], request["prompt"], region=region,
        )
    if operation == "image-to-3d":
        return lux3d_client.create_image_to_3d_task(
            request.get("img"),
            imgs=request.get("imgs"),
            version=request["version"],
            faceCount=request.get("faceCount"),
            outputFormat=request.get("outputFormat"),
            enablePbr=request.get("enablePbr"),
            aiPredictSize=request.get("aiPredictSize"),
            customSize=request.get("customSize"),
            region=region,
            content_id=content_id,
        )
    if operation == "text-to-3d":
        return lux3d_client.create_text_to_3d_task(
            request["prompt"],
            version=request["version"],
            style=request.get("style"),
            img=request.get("img"),
            faceCount=request.get("faceCount"),
            outputFormat=request.get("outputFormat"),
            enablePbr=request.get("enablePbr"),
            aiPredictSize=request.get("aiPredictSize"),
            customSize=request.get("customSize"),
            region=region,
            content_id=content_id,
        )
    if operation == "material-transfer":
        return lux3d_client.create_material_transfer_task(
            request["img"],
            request["meshUrl"],
            version=request["version"],
            outputFormat=request.get("outputFormat"),
            aiPredictSize=request.get("aiPredictSize"),
            customSize=request.get("customSize"),
            region=region,
            content_id=content_id,
        )
    if operation == "four-view":
        return lux3d_client.create_image_to_four_view_task(
            request.get("img"), prompt=request.get("prompt"), region=region, content_id=content_id
        )
    if operation == "mesh-retopology":
        return lux3d_client.create_mesh_retopology_task(
            request["modelUrl"], request["faceLimit"],
            quad=request.get("quad", True),
            bakeTextures=request.get("bakeTextures", False),
            textureSize=request.get("textureSize", 2048),
            region=region, content_id=content_id,
        )
    return lux3d_client.create_multi_format_export_task(
        request["modelUrl"],
        outputFormat=request.get("outputFormat"),
        region=region,
        content_id=content_id,
    )


def artifact_path(output_dir, basename, output_format, multiple):
    suffix = lux3d_client.output_extension(output_format)
    stem = f"{basename}_{output_format}" if multiple else basename
    return output_dir / f"{stem}.{suffix}"


def download_and_validate(state_path, state, outputs, *, actions, generation_port=None):
    request = state["request"]
    formats = state["expectedFormats"]
    if request["operation"] == "animation-retarget":
        key = "animationGlbUrl" if request["outFormat"] == "glb" else "fbxUrl"
        records_by_url = {}
        for action in actions:
            if action["status"] != "success":
                continue
            record = records_by_url.setdefault(action[key], {"url": action[key], "format": request["outFormat"], "actionIds": []})
            record["actionIds"].append(action["animation_id"])
        records = list(records_by_url.values())
    else:
        urls = lux3d_client.map_artifact_urls(outputs, formats)
        records = [{"url": urls[output_format], "format": output_format} for output_format in formats]
    output_dir = pathlib.Path(state["outputDir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = []
    try:
        for index, record in enumerate(records, 1):
            output_format = record["format"]
            if request["operation"] == "animation-retarget":
                stem = request["outputBasename"]
                if request["animationOutputMode"] == "separate":
                    stem += f"_action_{index:02d}"
                target = output_dir / f"{stem}.{lux3d_client.output_extension(output_format)}"
                inspection_options = {"require_rig": True, "require_animation": True, "minimum_animation_clips": len(record["actionIds"])}
            else:
                target = artifact_path(output_dir, request["outputBasename"], output_format, len(formats) > 1)
                inspection_options = {"require_rig": True} if request["operation"] == "auto-rig" else {}
            if request["operation"] == "articulation-animation":
                target = output_dir / (request["outputBasename"] +
                    lux3d_client.articulation_result_extension(record["url"]))
            temporary = target.with_name(f".{target.name}.part")
            if temporary.exists():
                temporary.unlink()
            try:
                downloaded_size = (
                    lux3d_client.download_model(
                        record["url"], str(temporary)
                    )
                    if generation_port is None
                    else generation_port.download(
                        record["url"], str(temporary)
                    )
                )
                if downloaded_size <= 0:
                    raise ValueError(f"Downloaded artifact is empty: {output_format}")
                if request["operation"] == "mesh-retopology" and output_format == "obj_zip":
                    lux3d_client.validate_retopology_download(str(temporary), output_format)
                if request["operation"] == "articulation-animation":
                    artifact_delivery.inspect_articulation_artifact(temporary, target.suffix)
                else:
                    artifact_delivery.inspect_artifact(temporary, output_format, **inspection_options)
                os.replace(temporary, target)
            finally:
                if temporary.exists():
                    temporary.unlink()
            artifact = {"path": str(target.expanduser().resolve()), "format": output_format}
            if "actionIds" in record:
                artifact["actionIds"] = record["actionIds"]
            artifacts.append(artifact)
            update_state(state_path, state, downloadedArtifacts=list(artifacts))

        inputs = {
            key: value
            for key, value in request.items()
            if key not in {"operation", "region", "version", "outputBasename", "target"}
        }
        spec = {
            "operation": request["operation"],
            "region": request["region"],
            "version": request.get("version"),
            "taskId": state["taskId"],
            "stepId": state["commerce"]["stepId"],
            "attemptId": state["commerce"]["attemptId"],
            "inputs": inputs,
            "artifacts": artifacts,
            "target": request["target"],
        }
        for key in ("actionResults", "completion"):
            if key in state:
                spec[key] = state[key]
        manifest = artifact_delivery.build_manifest(spec)
        if state.get("deliveryWarnings"):
            manifest["warnings"] = state["deliveryWarnings"]
        manifest_path = output_dir / DELIVERY_FILENAME
        artifact_delivery.write_json_atomic(manifest_path, manifest)
        update_state(
            state_path,
            state,
            status="succeeded",
            manifestPath=str(manifest_path.resolve()),
            lastError=None,
        )
        return state
    except (FileNotFoundError, ValueError, RuntimeError, TimeoutError) as exc:
        update_state(state_path, state, status="delivery_failed", lastError=str(exc))
        raise


def resume_workflow(
    state_path,
    max_attempts,
    interval,
    *,
    generation_port=None,
    submission_registry=None,
):
    state_path = pathlib.Path(state_path).expanduser().resolve()
    state = read_json(state_path)
    artifact_delivery.assert_no_secrets(state)
    if artifact_delivery.without_transient_urls(state) != state:
        update_state(state_path, state)
    migrate_legacy_state(state_path, state)
    if state.get("schema") != STATE_SCHEMA:
        raise ValueError(f"Unsupported workflow state schema: {state.get('schema')}")
    request = validate_persisted_request(state.get("request") or {})
    operation = request["operation"]
    if state.get("status") == "succeeded" and operation not in PREVIEW_OPERATIONS:
        return state
    if state.get("status") in {"failed", "cancelled"}:
        raise RuntimeError(f"Task is terminal with status {state['status']}: {state.get('lastError')}")
    if not state.get("taskId"):
        if state.get("status") == "submission_blocked":
            raise RuntimeError(
                f"Task submission was blocked before the API call: {state.get('lastError')}"
            )
        if state.get("status") == "submission_rejected":
            raise RuntimeError(
                f"Task submission was rejected by the API: {state.get('lastError')}"
            )
        if state.get("status") != "submission_unknown":
            raise RuntimeError("Workflow has no task ID and cannot be resumed")
        commerce = state.get("commerce") or {}
        if submission_registry is None:
            raise RuntimeError(
                "Task submission result is unknown. Query Lux3D task history and provide a SubmissionRegistryPort before deciding whether to create a new task."
            )
        try:
            record = submission_registry.lookup(
                unique_id=commerce.get("uniqueId"),
                request_key=commerce.get("requestKey"),
            )
        except Exception as exc:
            raise RuntimeError(
                "Submission registry lookup failed during reconciliation"
            ) from exc
        reconciled_task_id = record.get("taskId") if isinstance(record, dict) else None
        if (
            not isinstance(record, dict)
            or record.get("status") != "accepted"
            or not isinstance(reconciled_task_id, str)
            or not reconciled_task_id
        ):
            raise RuntimeError(
                "Task submission is still unknown. Query Lux3D task history before any new create request."
            )
        update_state(
            state_path,
            state,
            status="submitted",
            taskId=reconciled_task_id,
            registryHealth="ok",
            reconciledAt=utc_now(),
            lastError=None,
        )

    queryable_states = set(QUERYABLE_STATES)
    if operation in PREVIEW_OPERATIONS:
        queryable_states.add("succeeded")
    if state.get("status") not in queryable_states:
        raise ValueError(f"Workflow state is not resumable: {state.get('status')}")
    validate_generation_port_context(generation_port, state)

    update_state(
        state_path,
        state,
        status="running",
        queryHealth="querying",
        lastError=None,
    )
    try:
        outputs = generation_port.query(
            state["taskId"],
            region=request["region"],
            max_attempts=max_attempts,
            interval=interval,
            output_slots=fixed_output_slots(request),
        )
    except TimeoutError as exc:
        observed_status = getattr(exc, "last_provider_status", None)
        provider_status = (
            observed_status
            if observed_status is not None
            else state.get("lastKnownProviderStatus")
        )
        update_state(
            state_path,
            state,
            status="running",
            queryHealth="ok",
            lastKnownProviderStatus=provider_status,
            lastError=str(exc),
        )
        raise
    except RuntimeError as exc:
        message = str(exc)
        failure_facts = {}
        if isinstance(exc, lux3d_client.TaskTerminalError) and request["operation"] in {"auto-rig", "animation-retarget"} and exc.task_data:
            try:
                failed_outputs = lux3d_client.parse_task_outputs(exc.task_data)
                if request["operation"] == "animation-retarget" and isinstance(failed_outputs, dict) and "actions" in failed_outputs:
                    failure_facts["actionResults"] = lux3d_client.validate_animation_results(failed_outputs, request["animationIds"], outFormat=request["outFormat"], animationOutputMode=request["animationOutputMode"])
                elif isinstance(failed_outputs, dict) and isinstance(failed_outputs.get("error"), dict):
                    failure_facts["providerError"] = failed_outputs["error"]
            except (ValueError, RuntimeError) as output_error:
                failure_facts["outputError"] = str(output_error)
        if isinstance(exc, lux3d_client.TaskOutputError):
            update_state(
                state_path,
                state,
                status="output_invalid",
                queryHealth="ok",
                lastKnownProviderStatus=3,
                lastError=message,
            )
            raise
        if message.startswith("Task failed:"):
            status = "failed"
            query_health = "ok"
            provider_status = getattr(exc, "last_provider_status", 4)
        elif message.startswith("Task was cancelled:"):
            status = "cancelled"
            query_health = "ok"
            provider_status = 6
        else:
            # A failed query is transport health, not a provider state.
            # Preserve the last known task fact and make the health failure
            # independently resumable.
            status = "running"
            query_health = "error"
            observed_status = getattr(exc, "last_provider_status", None)
            provider_status = (
                observed_status
                if observed_status is not None
                else state.get("lastKnownProviderStatus")
            )
        update_state(
            state_path,
            state,
            status=status,
            queryHealth=query_health,
            lastKnownProviderStatus=provider_status,
            lastError=message,
            **failure_facts,
        )
        raise
    try:
        actions = validate_requested_provider_outputs(request, outputs, state["expectedFormats"])
    except lux3d_client.TaskOutputError as exc:
        update_state(
            state_path,
            state,
            status="output_invalid",
            queryHealth="ok",
            lastKnownProviderStatus=3,
            lastError=str(exc),
        )
        raise
    result_facts = {}
    if actions is not None:
        succeeded = [action["animation_id"] for action in actions if action["status"] == "success"]
        failed = [action["animation_id"] for action in actions if action["status"] == "failed"]
        result_facts = {"actionResults": actions, "completion": {"status": "partial" if failed else "complete", "successfulActionIds": succeeded, "failedActionIds": failed}}
    if operation == "articulation-animation":
        extension = lux3d_client.articulation_result_extension(outputs)
        state["expectedFormats"] = ["glb" if extension == ".glb" else "file"]
        state["deliveryWarnings"] = ["JOINT_MOTION_NOT_VERIFIED"]
    if operation == "mesh-retopology":
        # Optional ZIP follows actual provider output, not the original bake request.
        state["expectedFormats"] = [
            name for name in lux3d_client.RETOPOLOGY_OUTPUT_SLOTS if name in outputs
        ]
        state["deliveryWarnings"] = lux3d_client.retopology_result(
            state["taskId"], outputs, request.get("bakeTextures", False)
        )["warnings"]
    update_state(
        state_path,
        state,
        status="provider_succeeded",
        queryHealth="ok",
        lastKnownProviderStatus=3,
        artifactExpiresInSeconds=lux3d_client.ARTIFACT_TTL_SECONDS,
        lastError=None,
        **result_facts,
    )

    if operation == "four-view":
        if not isinstance(outputs, list) or len(outputs) != 4:
            update_state(
                state_path,
                state,
                status="delivery_failed",
                lastError="Four-view task did not return exactly four URLs",
            )
            raise RuntimeError("Four-view task did not return exactly four URLs")
        update_state(
            state_path,
            state,
            status="succeeded",
            artifactExpiresInSeconds=lux3d_client.ARTIFACT_TTL_SECONDS,
            lastError=None,
        )
        return {**state, "fourViewUrls": outputs}

    return download_and_validate(
        state_path, state, outputs, actions=actions, generation_port=generation_port
    )


def run_workflow(
    request_path,
    output_dir,
    state_path,
    max_attempts,
    interval,
    *,
    submission_gate=None,
    quote_verifier=None,
    submission_registry=None,
    generation_port=None,
):
    request = validate_request(read_json(request_path))
    submission_context = request["submission"]
    persisted_request = {
        key: value for key, value in request.items() if key != "submission"
    }
    output_dir = pathlib.Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    state_path = pathlib.Path(state_path).expanduser().resolve()
    state = {
        "schema": STATE_SCHEMA,
        "createdAt": utc_now(),
        "status": "awaiting_submission_gate",
        "taskId": None,
        "accountRef": submission_context["accountRef"],
        "environmentRef": f"lux3d:{request['region']}",
        "stage": "execution",
        "request": artifact_delivery.without_transient_urls(persisted_request),
        "commerce": workflow_contracts.persistable_submission_context(
            submission_context
        ),
        "expectedFormats": expected_formats(request),
        "outputDir": str(output_dir),
        "queryHealth": "not_queried",
        "lastKnownProviderStatus": None,
        "lastError": None,
    }
    create_state_exclusive(state_path, state)
    try:
        if quote_verifier is None:
            raise ValueError(
                "A trusted QuoteVerificationPort is required before a paid create request"
            )
        if submission_gate is None:
            raise ValueError(
                "A current-conversation SubmissionGate is required before a paid create request"
            )
        if submission_registry is None:
            raise ValueError(
                "A SubmissionRegistryPort is required before a paid create request"
            )
        if generation_port is None:
            raise ValueError(
                "A GenerationPort is required before a paid create request"
            )
        validate_generation_port_context(generation_port, state)
        intent = workflow_contracts.build_submission_intent(request)
        try:
            verification = quote_verifier.verify_submission(intent)
        except Exception as exc:
            raise RuntimeError(
                "Quote verification failed before the create request"
            ) from exc
        if not isinstance(
            verification, workflow_contracts.SubmissionVerification
        ):
            raise ValueError("QuoteVerificationPort returned an invalid result")
        if not verification.verified:
            raise ValueError("Trusted quote verification rejected this request")
        try:
            decision = submission_gate.authorize(intent)
        except Exception as exc:
            raise RuntimeError(
                "SubmissionGate failed before the create request"
            ) from exc
        if not isinstance(decision, workflow_contracts.SubmissionDecision):
            raise ValueError("SubmissionGate returned an invalid decision")
        if not decision.allowed:
            raise ValueError(
                "Current conversation does not confirm this submission"
            )
        if (
            not isinstance(decision.user_event_ref, str)
            or not re.fullmatch(r"[A-Za-z0-9._:-]{1,200}", decision.user_event_ref)
        ):
            raise ValueError(
                "SubmissionGate must return an opaque current-conversation user event reference"
            )
        update_state(
            state_path,
            state,
            status="submission_gate_passed_for_call",
            submissionCheck={
                "checkedAt": utc_now(),
                "decision": "allowed",
                "userEventRef": decision.user_event_ref,
                "reusable": False,
            },
            lastError=None,
        )
        try:
            reservation = submission_registry.reserve(intent)
        except Exception as exc:
            raise RuntimeError(
                "Submission registry failed before the create request"
            ) from exc
        if not isinstance(
            reservation, workflow_contracts.SubmissionReservation
        ):
            raise ValueError("SubmissionRegistryPort returned an invalid result")
        if not reservation.reserved:
            raise ValueError("Submission registry rejected a duplicate attempt")
    except (ValueError, RuntimeError) as exc:
        update_state(
            state_path,
            state,
            status="submission_blocked",
            lastError=str(exc),
        )
        raise
    try:
        task_id = generation_port.submit(
            workflow_contracts.generation_port_request(request)
        )
        if not isinstance(task_id, str) or not task_id.strip():
            raise RuntimeError(
                "GenerationPort returned no valid task ID after the create request"
            )
        task_id = task_id.strip()
    except lux3d_client.ApiBusinessRejection as exc:
        registry_health = finalize_submission_registry(
            submission_registry, intent, outcome="rejected"
        )
        update_state(
            state_path,
            state,
            status="submission_rejected",
            registryHealth=registry_health,
            lastError=str(exc),
        )
        raise
    except ValueError as exc:
        registry_health = finalize_submission_registry(
            submission_registry, intent, outcome="rejected"
        )
        update_state(
            state_path,
            state,
            status="submission_blocked",
            registryHealth=registry_health,
            lastError=str(exc),
        )
        raise
    except (RuntimeError, TimeoutError) as exc:
        registry_health = finalize_submission_registry(
            submission_registry, intent, outcome="unknown"
        )
        update_state(
            state_path,
            state,
            status="submission_unknown",
            registryHealth=registry_health,
            lastError=str(exc),
        )
        raise
    registry_health = finalize_submission_registry(
        submission_registry,
        intent,
        outcome="accepted",
        task_id=task_id,
    )
    update_state(
        state_path,
        state,
        status="submitted",
        taskId=task_id,
        submittedAt=utc_now(),
        registryHealth=registry_health,
        lastError=None,
    )
    return resume_workflow(
        state_path,
        max_attempts,
        interval,
        generation_port=generation_port,
        submission_registry=submission_registry,
    )


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run and resume verified Lux3D delivery workflows."
    )
    subparsers = parser.add_subparsers(dest="command")
    run = subparsers.add_parser("run")
    run.add_argument("--request", required=True)
    run.add_argument("--output-dir", required=True)
    run.add_argument("--state", required=True)
    for command in (run, subparsers.add_parser("resume")):
        if command.prog.endswith(" resume"):
            command.add_argument("--state", required=True)
        command.add_argument("--max-attempts", type=int, default=lux3d_client.DEFAULT_POLL_ATTEMPTS)
        command.add_argument("--interval", type=float, default=lux3d_client.DEFAULT_POLL_INTERVAL)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "run":
        result = run_workflow(
            args.request,
            args.output_dir,
            args.state,
            args.max_attempts,
            args.interval,
        )
    elif args.command == "resume":
        result = resume_workflow(args.state, args.max_attempts, args.interval)
    else:
        parser.print_help()
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, FileExistsError, ValueError, RuntimeError, TimeoutError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
