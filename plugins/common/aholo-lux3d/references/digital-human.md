# Character rigging and animation

Use auto-rigging to produce a rigged character GLB, or retargeting to apply selected public animations to an already rigged GLB. Local files follow the existing Asset upload flow before creation. Inputs must be real, publicly readable HTTPS GLB URLs without user info or fragments; do not quote a dependent step with a placeholder URL.

Read the shared `core/contracts/lux3d-generation.v1.json` for supported parameters and the versioned public animation IDs. Do not guess IDs from a motion description or use internal templates. Preserve their case and request order. Select 1–10 distinct, nonblank IDs; reject duplicates, unknown IDs and out-of-range counts before creation.

## Quote and create

| Operation | Public POST path | Business parameters |
| --- | --- | --- |
| `auto-rig` | `/lux3d/v1/animations/rig/task/create` | Required `modelUrl` |
| `animation-retarget` | `/lux3d/v1/animations/retarget/task/create` | Required `rigModelUrl`, `animationIds`; optional `animationOutputMode`, `outFormat`, `animateInPlace` |

Retargeting defaults to `animationOutputMode=separate`, `outFormat=glb` and `animateInPlace=false`. Mode is `separate` or `combined`; output is `glb` or bare `fbx`. `animateInPlace` must be a boolean, not the string `"false"`. Neither operation accepts a generation `version`.

Use the same normalized business body for [quoting and approval](review.md) and creation. Quote `items` contain these business parameters only. Add the current matching quote's `quoteId` as `content_id` on the actual create helper, which writes wire `contentId`. Do not substitute `uniqueId`, `pluginTaskId`, an older quote or a global last-quote value. This correlation field is not an authorization or idempotency key.

After the existing prerequisites and spending approval pass, use `create_auto_rig_task` or `create_animation_retarget_task` in `core/runtime/lux3d_client.py`, passing `region` and `content_id` explicitly. Their CLI entrypoints are `auto-rig <modelUrl>` and `retarget <rigModelUrl>`, with `--content-id <quoteId>`; retarget uses repeatable `--animation-id`, `--output-mode`, `--format`, and `--animate-in-place`. Read `--help` for actual arguments. Creation returns the remote task ID immediately: persist its exact decimal string before querying.

If acceptance is unknown, retain the original submission evidence and committed budget without another paid POST. Resume a known task by its saved ID using the shared query endpoint and the original region/account. Query or delivery errors never authorize regeneration.

## Rig, then animate

For a complete character workflow, quote and create rigging first. Wait for its successful result and inspect the actual rigged GLB. Use that real result URL to build the retargeting business body and obtain its own quote. Apply existing approval/budget scope to the second call and keep both quote IDs and provider task IDs under the same creative `pluginTaskId`. Failed rigging prevents the dependent retargeting call. Retargeting failure preserves the usable rigged asset; do not rig again to resume it.

## Read per-action results

The shared query returns statuses 0/1/2 while waiting, 3 for provider success, 4/5 for failure, and 6 for cancellation. Rigging success returns a GLB URL in `outputs[0].content`. Its failure may return a JSON object with `error.code` and `error.message`.

Retargeting `outputs[0].content` is a JSON string containing `actions`. Each item uses the formal `animation_id` and `status`. A success contains `animationGlbUrl` or `fbxUrl` for the requested format. A failure contains its real `error.code` and `error.message`. Keep every requested action's result exactly once; reject missing, duplicate, unknown or malformed results rather than fill them with success. A provider status of 3 can include failed actions. All-action failure must still preserve error details.

Present partial completion explicitly alongside available files. Keep the actual provider status separate from download, validation and preview results. Store sanitized `actionResults` and completion facts in the task records; do not copy temporary signed URLs into portable delivery records or reports.

## Inspect and deliver

`separate` gives one complete file per successful action, including several files of the same format. Use distinct paths and artifact identities; associate each file with its real `actionIds`. `combined` may return the same URL for several successful actions: download that exact returned URL once and retain all associated actions. Do not infer correspondence from URL suffixes, output array position or guessed names.

Both operations require a GLB with valid skeleton and skin data. Retargeted GLB also requires valid animation channels; combined output retains independent clips. Bare FBX is not `fbx_zip`, and an intermediate GLB cannot replace a failed FBX delivery. Inspect FBX with a real reader or Blender readback, checking model, armature, skin and animation. Configure an available Blender executable through `LUX3D_BLENDER_EXECUTABLE` or the process PATH. If no reader is available or validation fails, keep provider success and state the delivery gap instead of marking the file verified.

For direct inspection, run `core/runtime/artifact_delivery.py inspect <file> --format glb --require-rig` for rigging. Retargeted files add `--require-animation` and use the actual `--format glb` or `--format fbx`; combined files add `--minimum-animation-clips <successful-action-count>`. The delivery bundler also enforces these digital-human checks. Ordinary structural inspection without the rig/animation flags does not prove character readiness.

Follow [Results and delivery](results.md) for the unified bundle and isolated preview validation. The offline GLB viewer plays, pauses and selects clips read from the actual file. Public results do not expose a `clipName` mapping, so do not guess which action corresponds to an internal clip name. FBX is delivered as its original file for the target DCC; this workflow does not add a browser FBX player.

Close out the factual execution report, including partial results and delivery gaps, through the existing collection workflow. Reporting failure does not block available files; optional experience feedback keeps its separate consent requirement.
