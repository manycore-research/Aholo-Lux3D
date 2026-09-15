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
- The model delivery reader does not package PNG/JPEG artifacts. Keep four-view images outside `downloadedArtifacts` and use an empty `expectedFormats` for a four-view snapshot. When they are intermediate inputs, include the resulting 3D assets in model delivery. For an image-only four-view request, deliver the verified image files directly; do not create an unrequested 3D model to satisfy the bundler.

Use portable item/attempt IDs of at most 80 ASCII letters, digits, hyphens or underscores, beginning with a letter or digit. Reuse the same attempt ID and state file for repeated instances of one generated asset. Do not invent missing facts to satisfy validation.

Use the user's chosen name or the model's subject as the title, preserving user-provided names and filenames. Choose the page language from the user's explicit preference or the current conversation: `zh-CN` for Chinese, and `en` for English, other languages, or an unspecified language. Use a new delivery directory to preserve earlier versions.

The page shows local end-to-end time for each attempt, not credits. Use the tool-recorded `localDurationMs`; leave missing values unavailable. Do not substitute server execution time or page rebuild time, or sum the durations of parallel tasks. Quotes and spending approval still follow [Review and approval](review.md).

## Preserve local modeling provenance

For an assembled architectural scene, include the selected shell and its contents in the exported `scene.glb`. Bind actual Lux3D source artifacts, including a Lux3D-generated shell when used, through the existing scene evidence contract. For Blender-built geometry, retain its construction script and execution record separately. Do not invent a Lux3D task ID or generation attempt for locally modeled geometry. The current bundle requires real generation items and source bindings; a purely local Blender scene cannot be represented by fabricated cloud records. Deliver its verified local files directly. A Blender-rendered still may accompany them as a clearly labeled static preview; do not present it as an interactive model viewer. If interactive preview is required and no supported route is available, report that gap instead.

## Deliver rendered media and Blender files

The current delivery bundler packages supported model artifacts and an optional `scene.glb`; it does not package rendered images, video, or Blender project files. Keep those outputs in a separate, clearly named delivery folder alongside the generated model bundle and link to them directly. Do not put them into `downloadedArtifacts`, invent manifest fields, or describe them as embedded in `preview.html`.

Inspect images and video as described in [Scene assembly and rendering](assembly.md). Deliver the planned media and any requested `.blend` file with its needed resources packed or included. Keep earlier versions available. If a render is unfinished, deliver usable models and state what remains; if only model packaging failed, preserve and deliver the verified media independently.

## Present the result

Read the existing manifest fields separately: `assetStatus` and item/attempt states describe model files, `scene.status` describes assembly, and `preview.status` describes the page. The current bundler leaves top-level `status` as `incomplete` even when all model files and the preview are available; that value alone does not establish generation failure. Report the actual files and checks without rewriting the manifest to manufacture overall acceptance. Assess requested Blender media separately: model and preview readiness does not establish that a shot is complete. Use these facts to give a concise task-level result; explain internal status fields only when they affect use of the files or the user asks.

Provide links or paths to the model files, `lux3d-delivery.json`, and the unified `preview.html` in the delivery bundle. Independent and assembled models share one preview page. Do not automatically open the preview page for the user; open it when requested. Delivery validation may use an isolated or headless viewer without taking over the user's browser. Verify actual model loading and interaction when that capability is available; otherwise state that interactive behavior was not verified. Provide original files even when their format cannot be previewed.

Make the model preview the first delivery link when it is available, on its own bullet with a prominent, descriptive label. Localize a label such as "Open model preview — complete scene and individual assets" to the user's language and the actual contents. Follow it with one short sentence explaining verified actions, such as rotating and zooming the scene or switching to individual assets. Do not bury this entry beside a still image or manifest under a generic "interactive preview" label. Do not claim that every deliverable is inside the viewer: rendered media and Blender projects are separate files.

Describe only the assets and controls actually included and verified. Scene object counts are not preview-item counts; do not promise per-object selection, layer controls, or separate asset views merely because objects exist in the scene. If the preview is incomplete, unavailable, or unverified, state that limitation and prioritize usable deliverables rather than presenting it as a complete working entry point.

After the preview, link the complete model and any planned Blender project, briefly explaining their purpose (importing into 3D software or continuing scene editing). Put supporting still images and the delivery manifest afterward. Preserve the visibility of a requested rendered image or video as a primary deliverable. Keep model limitations and quoted budget information separate from the file links.

For completed work, provide the files that fulfill the planned deliverables. For partial success, identify usable files and missing models, scenes, or renders. For running work, report actual progress. If no usable model is available, explain the failure and recovery conditions, then stop this attempt. Do not claim checks that were not performed or invent unknown charges or timings. Saving and delivering files does not depend on the user accepting them first.

## Revisions and project integration

For revisions, use [Understanding and planning](planning.md) to identify the target, version, and scope. Requested regeneration or additional candidates require a new quote and the applicable approval. Deliver all usable candidates the user requested. Once they select a version, replace only the relevant objects.

Integrate models into a downstream project only when requested. Follow its existing loaders, asset directories, naming, and build conventions, and report the integration and checks actually completed.
