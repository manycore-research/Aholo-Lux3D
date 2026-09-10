# Results and delivery

Deliver models based on actual task states, files, and inspection results. Preview failure does not trigger regeneration.

## Inspect files

Use `inspect` in `core/runtime/artifact_delivery.py` when model files need validation. Read its `--help` for arguments. Passing structural checks does not establish that the objects, versions, or assembly layout meet the request; verify those against the actual models. Download temporary outputs promptly and preserve the original files and workflow records.

## Prepare the delivery bundle

Use `prepare` in `core/runtime/delivery_bundle.py`. Read its `--help` for arguments. Prepare the input using `core/contracts/examples/delivery-spec.json`, identifying the version to deliver and real file references. Read `core/contracts/task-metadata.md` for task creation metadata and local end-to-end timing. For assembled models, also read `core/contracts/scene-delivery.md`.

For tasks submitted through the client API, create each referenced `statePath` from the actual local attempt record and query/download results. The existing reader in `core/runtime/delivery_bundle.py` accepts a delivery snapshot with `schema: lux3d.workflow-state/v2`, the real `taskId`, `status`, `lastKnownProviderStatus`, a sanitized `request`, `expectedFormats`, and `downloadedArtifacts`. This is input to the delivery reader, not a complete runner execution record or proof that its submission checks ran. Keep private approval/quote records separate.

- In `request`, use the operation identifiers `text-to-3d`, `image-to-3d`, `material-transfer`, `four-view`, or `export`, and the actual `region`. Include the actual `version` for the first three; omit it for four-view and export.
- Use the output helpers in [Execution and recovery](execution.md) for `expectedFormats`. Each `downloadedArtifacts` entry has a real `path` (absolute or relative to its state file) and a supported `format`. Keep format identifiers such as `obj_zip` and `fbx_zip` even though their filenames end in `.zip`.
- Use the documented runtime status names. For success, set `status: succeeded` and `lastKnownProviderStatus: 3` only after all expected model artifacts have been downloaded and inspected. Preserve known provider status separately from query or delivery errors. If the submission outcome is unknown and no task ID is available, use `submission_unknown`, not an invented ID or an unsupported `unknown` status.
- Record actual timezone-qualified `createdAt`, `updatedAt`, and the first `localCompletedAt` where known. The delivery tool computes `localDurationMs`; preserve these timestamps across preview rebuilds. Omit unknown times.
- Four-view images are intermediate inputs. The model delivery reader does not package PNG/JPEG artifacts: keep them outside `downloadedArtifacts` and use an empty `expectedFormats` for a four-view snapshot. Include the resulting 3D assets in the model delivery.

Use portable item/attempt IDs of at most 80 ASCII letters, digits, hyphens or underscores, beginning with a letter or digit. Reuse the same attempt ID and state file for repeated instances of one generated asset. Do not invent missing facts to satisfy validation.

Use the user's chosen name or the model's subject as the title, preserving user-provided names and filenames. Choose the page language from the user's explicit preference or the current conversation: `zh-CN` for Chinese, and `en` for English, other languages, or an unspecified language. Use a new delivery directory to preserve earlier versions.

The page shows local end-to-end time for each attempt, not credits. Use the tool-recorded `localDurationMs`; leave missing values unavailable. Do not substitute server execution time or page rebuild time, or sum the durations of parallel tasks. Quotes and spending approval still follow [Review and approval](review.md).

## Present the result

Read the existing manifest fields separately: `assetStatus` and item/attempt states describe model files, `scene.status` describes assembly, and `preview.status` describes the page. The current bundler leaves top-level `status` as `incomplete` even when all model files and the preview are available; that value alone does not establish generation failure. Report the actual files and checks without rewriting the manifest to manufacture overall acceptance.

Provide links or paths to the model files, `lux3d-delivery.json`, and the unified `preview.html` in the delivery bundle. Independent and assembled models share one preview page. Do not open it automatically; use an available viewer only when the user asks to view it. Provide original files even when their format cannot be previewed.

For completed work, provide the files. For partial success, identify usable and missing models. For running work, report actual progress. If no usable model is available, explain the failure and recovery conditions, then stop this attempt. Do not claim checks that were not performed or invent unknown charges or timings. Saving and delivering files does not depend on the user accepting them first.

## Revisions and project integration

For revisions, use [Understanding and planning](planning.md) to identify the target, version, and scope. Requested regeneration or additional candidates require a new quote and the applicable approval. Deliver all usable candidates the user requested. Once they select a version, replace only the relevant objects.

Integrate models into a downstream project only when requested. Follow its existing loaders, asset directories, naming, and build conventions, and report the integration and checks actually completed.
