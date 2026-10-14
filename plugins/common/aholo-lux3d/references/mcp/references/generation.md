# Model processing and character animation through MCP

Use the exact tools in the [tool map](../tool-map.json). The four tools were
verified in the published `lux3d-mcp` 1.1.3 configuration, using generation
MCP 1.0.4. [Generation tool schemas](../generation-tools.json) preserves that
configuration as reference evidence. Discover the current session's actual
schemas and verify account access on the selected regional connection before quoting or creating; a published
configuration does not prove this host's authentication or tool availability.

## Inputs, quotes and creation

Prepare all model inputs through [Asset/OUS](upload.md). Quote the canonical
OpenAPI path in the map. The MCP server owns its internal SOA routing; do not
put `/api/open/...` paths, a service VIP or the MCP URL in quote items or tool
arguments. Neither a public OpenAPI path nor an internal route is an MCP tool.

The published create schema wraps the JSON object in `body`. For example,
articulation uses `{"body":{"glbUrl":"<uploaded GLB URL>","prompt":"<motion instruction>"}}`.
Use an object for create, not the serialized body string used in quote
parameters. None of these four operations accepts a generation `version`.

| Operation | Required business fields | Optional business fields |
| --- | --- | --- |
| `mesh-retopology` | `modelUrl`, `faceLimit` | `quad`, `bakeTextures`, `textureSize` |
| `articulation-animation` | `glbUrl`, `prompt` | None; additional fields are rejected |
| `auto-rig` | `modelUrl` | None |
| `animation-retarget` | `rigModelUrl`, `animationIds` | `animationOutputMode`, `outFormat`, `animateInPlace` |

Keep the normalized business body identical between quotation and creation.
For retopology, auto-rig and retargeting, add the matching returned `quoteId`
as `body.contentId` at creation when accepted by the discovered schema. It is
trace metadata, not an idempotency key. Retain it locally for recovery.
Articulation rejects `contentId`, `quoteId`, `uniqueId`, `source`, `agentName`
and all other extra body fields; retain quote and identity only in host state.

### Retopology

Input must be a static, non-Draco GLB. Multiple meshes are processed as one
model; original part boundaries are not guaranteed. `quad` defaults to true;
`faceLimit` must be an integer from 1,000 to 500,000 for quad, or 2,000 to
1,000,000 for triangle output. The count is an algorithm budget, not a promise
of an exact number of output faces. GLB remains triangulated even with quad OBJ.
`bakeTextures` defaults to false; `textureSize` is 512, 1024, 2048 or 4096,
default 2048. Do not pass internal strategy or topology engine parameters.

### Articulation

`glbUrl` must point to the uploaded GLB. `prompt` must be nonblank and describe
the moving parts and desired motion. The input URL need not end in `.glb` if
the upload receipt proves its content. Do not convert a successful upload URL
into a guessed path. This capability creates joints and motion for model parts;
it does not substitute for humanoid bone rigging.

### Auto-rig and retargeting

Use auto-rig for a character GLB; use retargeting on an already rigged GLB.
Model URLs must be usable HTTPS GLB inputs. Preserve a completed rig if a later
animation step is blocked. A dependent retarget quote uses the real returned
rig URL after upload preparation, not a placeholder URL or the unrigged input.

Read [animation-ids.json](../animation-ids.json). Select 1–10 distinct IDs from
the 85-item catalog, preserving case and request order. Do not invent IDs from
natural-language motion descriptions. `animationOutputMode` is `separate`
(default) or `combined`; `outFormat` is `glb` (default) or bare `fbx`;
`animateInPlace` is a boolean, default false. Multiple actions belong to one
create request, not one billable create per action. Combined output keeps an
independent animation clip per action; it is not necessarily one timeline.

## Query, recover and deliver

Create once, persist the exact returned task ID as a decimal string, then use
`gettask`. Follow [execution and recovery](execution.md) for uncertain
submission, polling and download failures. All four operations share the
account's generation concurrency quota. Do not create again to recover a query
or download, and do not promise a cancellation or refund without service evidence.

Use the actual task response, including `outputs[*].content`, rather than
assuming every result is a plain GLB URL. Check terminal status and business
errors; creation acceptance or HTTP 200 alone is not successful generation.

| Operation | Result handling |
| --- | --- |
| Retopology | Fixed GLB, OBJ, OBJ ZIP order. GLB and OBJ are required; ZIP may be the empty string. Deliver geometry and disclose missing baked textures if requested. Do not shift slots or use the input URL as a fallback result. |
| Articulation | One artifact URL. Preserve its actual format and original file extension; it may be GLB, ZIP or another format. Do not assume a ZIP contains a GLB or rename arbitrary bytes to `.glb`. Download or container checks do not prove correct joint motion. |
| Auto-rig | Success returns the rigged GLB URL. A terminal error may be encoded as a JSON object string with `error.code` and `error.message`. A task ID or source model is not a rigged deliverable. |
| Retargeting | Parse the JSON object string containing `actions`. Match `animation_id` against the requested IDs. Successful GLB actions use `animationGlbUrl`; FBX actions use `fbxUrl`. Preserve failed actions and their `error` details even when provider task status is success. |

For separate retarget output, retain each successful action file and its action
ID. For combined output, deduplicate the shared file URL while retaining every
action record. Missing or contradictory action results are a delivery gap,
not permission to label all requested motions successful. Deliver available
successes and explicitly identify partial completion. Motion clip names cannot
be mapped to action IDs unless the service provides that mapping.

Provide genuine download links or verified local files using host capabilities.
Do not claim motion playback, offline preview, skeleton inspection or Blender
scenes unless the host actually produced and checked them. FBX delivery does not
imply a browser FBX player. Final result links do not require re-upload unless
used as inputs to a later generation step.
