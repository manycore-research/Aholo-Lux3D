# Understanding and planning

Use the user's goal and the input requirements of the currently exposed Lux3D capabilities to decide whether there is enough information to plan. If there is, make the plan autonomously; otherwise, resolve only the necessary gaps. Produce an executable plan with known costs for the relevant work. Reuse information, plans, and models that still apply.

## Understand the goal and constraints

Use the current request, existing plan, models, and tasks to identify the operation, target, version, and scope. Treat follow-up information and approvals as part of the original request. A local revision does not imply rebuilding everything. Answer ordinary conversation directly.

Assess two independent dimensions:

- **Clarity:** If there is no concrete goal, offer a few directions. If the goal is clear but details are open, make reasonable choices about shape, style, and materials. If the information is sufficient, proceed to planning.
- **Model structure:** Distinguish a single object, a batch of independent assets, an assembled model, and a model generated as a whole that contains multiple objects. Assembly includes both scene composition and multipart construction. Identify requirements for independent editing and assembly; neither a singular subject name such as "a house" nor a single reference image establishes that the subject should be generated as one asset. File count alone does not determine the structure.

Preserve explicit requirements for use, subject, quantity, style, dimensions, format, privacy, and content. Keep the current agreed constraints with the task plan, including asset separation, reference fidelity, and any prohibition on simplification. A follow-up changes only the requirements it addresses; carry all others forward through replanning and context compression. For example, "make it look more like the reference" does not cancel "build the house and furniture separately." Independent editability and visual fidelity are separate requirements, not alternative production modes. Before executing a revised plan, check it against these retained constraints. Resolve an actual conflict with the user; do not add a routine reconfirmation step. Treat details you add as design assumptions, not replacements for the user's requirements. Distinguish layout, material, and geometry changes from regeneration or additional candidates. For running tasks, first check their status using [Execution and recovery](execution.md).

## Recognize architectural scenes and divide the work

For buildings, rooms, furnished interiors, and cutaway displays, inspect the request and reference for spatial structure and distinct contents before choosing generation calls. Recognize floors, room boundaries, openings, circulation, furniture, fixtures, vegetation, and other meaningful objects even when the user names only the building. A single image may describe an entire scene. Do not pass a furnished building or room to one generation call merely because it occupies one image or has one name.

For an architectural scene with distinct contents, keep the architectural shell separate from furniture and other discrete assets unless the user explicitly requests one fused asset. A request for one output file alone does not remove this separation. Prefer G1-Turbo for the architectural shell, especially when reference fidelity, multiple levels, or rich architectural detail matters. Use the routing guidance below for exceptions; Lux3D generates the discrete contents and Blender assembles them. Blender primarily handles assembly, precise components, and necessary local corrections in this route. The shell includes geometry whose dimensions and alignment organize the scene, such as walls, floors, roof, openings, stairs, and railings. Assign structural versus decorative details by their role and the required control rather than an exhaustive object list. Reuse suitable existing assets. A distant exterior-only building or a single manufactured object shaped like a house may remain one Lux3D asset when that satisfies the request; do not invent furnished interiors or force scene decomposition in those cases.

Choose a practical asset breakdown based on visibility, independent placement or editing, repeated instances, quality, and cost. Keep major furniture and distinctive props separate from the shell. Small decorative arrangements may be grouped when independent control is unnecessary; do not split every brick, leaf, or book into a paid generation. Reuse repeated assets without forcing visibly different designs to share one model. If cost or capability limits the plan, explain the tradeoff. Adjust only details left to your judgment; do not silently simplify required features or fuse contents that must remain separate.

Retain the full reference for layout and style, and prepare each generation input for the intended asset. Use a suitable isolated reference when available, or an asset-specific text description when the visible evidence supports one; do not send the same full-room image for every furniture item and expect isolation. Treat occluded geometry and unknown dimensions as assumptions, asking only when they materially affect the result. A cutaway reference calls for an open display of the intended rooms, not a facade that hides them.

Make the division visible in the production plan: identify what Blender will build, what Lux3D will generate, what will be reused, and how the parts relate by level, room, scale, and placement. Choose the detailed geometry and asset count autonomously. Check Blender availability before committing to the hybrid route, then follow [Scene assembly and rendering](assembly.md).

## Plan the requested deliverables

Distinguish asset files, an assembled scene, a still image, and an animated shot. A request describing camera movement, occlusion, or parallax should lead to a plan for the shot itself, including animation and rendered video, unless the user asks only for its assets. Preserve explicit deliverables and make reasonable choices for unspecified duration, framing, lighting, resolution, and frame rate; include material assumptions in the plan without adding a separate approval round.

Lux3D supplies generated assets. The host agent operates Blender for any planned local modeling, assembly, lighting, cameras, animation, and rendering through [Scene assembly and rendering](assembly.md). Check for a usable local Blender or Blender MCP route before promising Blender outputs. Missing MCP alone is not a blocker. Plan ahead when setup is pending, identify the unresolved prerequisite, and do not silently reduce a shot request to a collection of models.

Specify which files fulfill the goal: model files and `scene.glb` for an assembled scene, rendered images for a still, and video for a shot. Preserve a `.blend` working file for lighting, camera, and animation work so it can be resumed; deliver it when requested or included in the plan. The current offline page previews models; rendered media are delivered separately. Local Blender work consumes no Lux3D generation credits, but rendering time depends on scene complexity and available hardware. Any external paid rendering service requires separate authorization.

## Resolve gaps using the available capabilities

Use the currently exposed tool or command documentation to determine what can actually be called. As needed, read the relevant operation in `core/contracts/lux3d-generation.v1.json` for model versions, required inputs, optional parameters, and format limits. Combine this with information about existing models to assess feasibility. See [Execution and recovery](execution.md) for entrypoints and integration limits. An interface listed in a contract is not necessarily exposed for use.

For each capability's required inputs, distinguish information already available, details you can infer or generate in an earlier step, and information only the user can provide. Check documentation before asking about unclear capabilities or parameters. If a capability is unsupported or its entrypoint is unavailable, explain the limitation instead of repeatedly asking the user for more information.

Proceed when the goal, target, scope, and constraints that affect the plan are clear enough, and the remaining details can reasonably be filled in. Ask only about ambiguities, conflicting constraints, missing materials, or consequential choices that require the user to decide. Group necessary questions and wait for the answer. Do not require a parts list, generation sequence, or complete parameter set from the user, or add a separate requirements-approval step.

If a gap only affects later execution, plan ahead and mark the input as pending. Use follow-up information to resolve that gap; keep the plan when the user is simply supplying an agreed input. Apply the same rules if a new requirements gap appears during planning.

## Choose the approach and prepare parameters

Decide which assets or parts to generate separately, reuse, or process as a whole. Choose from the text-to-3D, image-to-3D, four-view, material-processing, and format-conversion capabilities that Lux3D actually exposes. Arrange inputs, dependencies, layout, and delivery. Prepare parameters directly for simple requests; break complex models into steps. Repeated instances do not require repeated generation, and material processing cannot replace a geometry change.

For text-only inputs to a Lux3D-generated asset, use Lux3D text-to-3D. Choose the architectural shell route independently as described above. Do not ask for an image merely because none was supplied. Ask for reference material only when the request depends on a specific reference the user must provide.

Distinguish ten different chairs from ten instances of the same chair. Multiple objects do not always need separate generation. Generating them as a whole does not guarantee independent editability, connected geometry, or printability.

Honor explicit user choices. Otherwise, autonomously choose the generation model, target face count, and optional steps such as four-view enhancement by weighing the asset's intended use, visual importance, available reference material, overall quality goals, cost, and speed against actual capabilities. Use tool defaults where appropriate. Four-view enhancement is optional, with no default preference for enabling or disabling it: decide whether its expected contribution to the current asset justifies the additional work and cost; do not assume it always improves the result. When information is sufficient, make these decisions without asking about each parameter. Include the choices and their costs in the plan and quote, and present them together when the selected approval mode calls for review.

Use these routing tendencies as starting points, not guarantees or fixed complexity thresholds. Preserve explicit user choices and adjust based on inspected results:

| Route | Prefer considering it for | Inspect especially |
| --- | --- | --- |
| G1-Turbo | Preferred starting route for architectural shells, especially reference-driven or detailed buildings; other complex structures with multiple levels, openings, or intricate spatial relationships | Structural completeness, orientation, and material fidelity |
| G1 | Relatively simple geometry whose appearance depends strongly on materials and surface detail | Surface detail, silhouette, and local geometry |
| Blender | Simple volumes, regular components, and geometry needing precise dimensions or alignment | Proportions, dimensions, connections, and layout |

For a generated architectural shell, inspect its silhouette, floor count, openings, left/right relationships, and usable interior space before fitting contents. Correct the specific defect where feasible; a local defect alone is not a reason to rebuild the whole shell in Blender. Simple shells or precisely dimensioned structures may still favor Blender, while relatively simple geometry dominated by surface detail may favor G1. Both generation tiers require visual inspection. If the chosen route misses the required result, revise the affected asset's approach while preserving separation and other agreed constraints. Choosing G1-Turbo does not imply enabling four-view enhancement; decide that separately. Four-view inputs require the consistency check in [Execution and recovery](execution.md) before use.

Use the localized generation-tier labels defined in [Review and approval](review.md), with only one language per label. Keep `G1` and `G1-Turbo` unchanged in API parameters and quote requests. Record the four-view choice, target face count or service default, and delivered formats for each asset so [Review and approval](review.md) can display the complete plan table.

Different assets in the same plan may use different generation models and parameters. Apply the considerations above to each asset rather than impose a fixed tier, face-count threshold, or enhancement choice across the plan.

Prepare and validate parameters against the actual capability. For outputs of future steps, record the source dependency and fill in the real reference when it becomes available. This does not prevent planning ahead.

Choose model formats for the intended use and explicit user requirements, checking the selected operation's supported outputs and any needed conversion. Do not request ZIP for every asset by habit. A service-required archive may still be returned; keep it as an additional source package rather than label it as a model format. Include required conversion costs in the quote and retain a GLB for the model preview when the plan requires one.

## When a plan is ready

An executable plan identifies the following. A short description is enough for a simple task; no fixed form is required.

- **Scope:** Models, quantities, revision targets, and what will be preserved.
- **Approach:** Capabilities and generation models, parts to model in Blender, assets to generate or reuse, and required processing or assembly steps.
- **Inputs and parameters:** Material sources and required parameters, including the sources of pending or future inputs.
- **Sequence and dependencies:** Execution order and dependencies, plus layout or part relationships when assembly is needed.
- **Delivery:** Models, assembled files, and requested images or video, with the relevant shot and output settings.

Once the plan can be executed and the relevant billable steps have real quotes, follow [Review and approval](review.md). For staged plans, advance only the work whose scope and costs are known, and identify what remains undecided.

## Use tools as needed

### Upload local inputs

When a local input needs an accessible URL, use `upload` in `core/runtime/asset_uploader.py`. Read its `--help` for arguments. On success, use the returned `url` as the service input and retain the local source file.

### Obtain a quote

Use `quote` in `scripts/commerce.py` when costs are needed. Read its `--help` for arguments. Prepare real requests for the selected capabilities. The quote file contains only a sequence map of billable calls, with no account or `items` wrapper. See `quotePlan.items` in `core/contracts/lux3d-commerce.v1.json` for its structure.

The command validates the quote-file structure, refreshes the account, and requests a quote; no separate balance query is needed first. A successful quote does not replace checks on generation parameters and actual inputs before submission. The response contains `account` and `quote`; use the itemized costs, total, and validity period in `quote`. Include billable prerequisites and follow-up processing. If future inputs affect pricing, quote in stages and explain which costs remain unknown.

`quote.details` maps the original numeric sequence keys to credit amounts; it does not contain asset labels or parameter descriptions. Retain that sequence-to-plan mapping to display costs against the correct assets. Each quote accepts 1–50 calls; split larger plans into quote groups and retain the full plan total. A later balance refresh that changes `uniqueId` invalidates quotes from the earlier context, even if their printed expiry has not passed.

## Continue from the result

- Correct parameter errors locally and retry the relevant tool. Update the plan only when the capability, asset breakdown, steps, or delivery requirements change. Stop if the same error repeats without new information.
- After a successful quote, use [Review and approval](review.md) to decide whether execution can proceed. Obtain a new quote when parameters, quantities, accounts, or pricing conditions change, or when the quote expires.
- A quote is an estimate before entitlements are applied, not the settled charge. Even a valid zero estimate does not guarantee free execution. Never treat failed or unknown costs as zero. Pause billable work if its cost cannot be quoted.
- Handle credentials and other call failures through [Execution and recovery](execution.md). Planning and quoting do not submit generation tasks.
