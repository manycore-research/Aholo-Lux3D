# Understanding and planning

Use the user's goal and the input requirements of the currently exposed Lux3D capabilities to decide whether there is enough information to plan. If there is, make the plan autonomously; otherwise, resolve only the necessary gaps. Produce an executable plan with known costs for the relevant work. Reuse information, plans, and models that still apply.

## Understand the goal and constraints

Use the current request, existing plan, models, and tasks to identify the operation, target, version, and scope. Treat follow-up information and approvals as part of the original request. A local revision does not imply rebuilding everything. Answer ordinary conversation directly.

Assess two independent dimensions:

- **Clarity:** If there is no concrete goal, offer a few directions. If the goal is clear but details are open, make reasonable choices about shape, style, and materials. If the information is sufficient, proceed to planning.
- **Model structure:** Distinguish a single object, a batch of independent assets, an assembled model, and a model generated as a whole that contains multiple objects. Assembly includes both scene composition and multipart construction. Identify requirements for independent editing and assembly; file count alone does not determine the structure.

Preserve explicit requirements for use, subject, quantity, style, dimensions, format, privacy, and content. Treat details you add as design assumptions, not replacements for the user's requirements. Distinguish layout, material, and geometry changes from regeneration or additional candidates. For running tasks, first check their status using [Execution and recovery](execution.md).

## Resolve gaps using the available capabilities

Use the currently exposed tool or command documentation to determine what can actually be called. As needed, read the relevant operation in `core/contracts/lux3d-generation.v1.json` for model versions, required inputs, optional parameters, and format limits. Combine this with information about existing models to assess feasibility. See [Execution and recovery](execution.md) for entrypoints and integration limits. An interface listed in a contract is not necessarily exposed for use.

For each capability's required inputs, distinguish information already available, details you can infer or generate in an earlier step, and information only the user can provide. Check documentation before asking about unclear capabilities or parameters. If a capability is unsupported or its entrypoint is unavailable, explain the limitation instead of repeatedly asking the user for more information.

Proceed when the goal, target, scope, and constraints that affect the plan are clear enough, and the remaining details can reasonably be filled in. Ask only about ambiguities, conflicting constraints, missing materials, or consequential choices that require the user to decide. Group necessary questions and wait for the answer. Do not require a parts list, generation sequence, or complete parameter set from the user, or add a separate requirements-approval step.

If a gap only affects later execution, plan ahead and mark the input as pending. Use follow-up information to resolve that gap; keep the plan when the user is simply supplying an agreed input. Apply the same rules if a new requirements gap appears during planning.

## Choose the approach and prepare parameters

Decide which assets or parts to generate separately, reuse, or process as a whole. Choose from the text-to-3D, image-to-3D, four-view, material-processing, and format-conversion capabilities that Lux3D actually exposes. Arrange inputs, dependencies, layout, and delivery. Prepare parameters directly for simple requests; break complex models into steps. Repeated instances do not require repeated generation, and material processing cannot replace a geometry change.

For a text-only request, use Lux3D text-to-3D. Do not ask for an image merely because none was supplied. Ask for reference material only when the request depends on a specific reference the user must provide.

Distinguish ten different chairs from ten instances of the same chair. Multiple objects do not always need separate generation. Generating them as a whole does not guarantee independent editability, connected geometry, or printability.

Honor explicit user choices. Otherwise, choose the generation model, parameters, and optional steps such as four-view enhancement using the requirements and actual capabilities. Use tool defaults where appropriate. Include these choices in the plan and quote instead of asking about each one in advance. When the selected approval mode calls for review, present them together for confirmation or revision.

Use the user-facing tier names Standard edition (Standard) for `G1` and Turbo edition (Turbo) for `G1-Turbo`, localizing the edition name into the user's language. Keep `G1` and `G1-Turbo` unchanged in API parameters and quote requests. Record the four-view choice, target face count or service default, and delivered formats for each asset so [Review and approval](review.md) can display the complete plan table.

Balance quality, cost, and speed for each asset. Use fast generation to validate an overall concept or produce assets with modest detail requirements. Use detailed generation for prominent assets or those requiring rich detail. Different assets in the same plan may use different capabilities; choose only supported models and parameters.

Prepare and validate parameters against the actual capability. For outputs of future steps, record the source dependency and fill in the real reference when it becomes available. This does not prevent planning ahead.

## When a plan is ready

An executable plan identifies the following. A short description is enough for a simple task; no fixed form is required.

- **Scope:** Models, quantities, revision targets, and what will be preserved.
- **Approach:** Capabilities and generation models, assets to generate or reuse, and required processing or assembly steps.
- **Inputs and parameters:** Material sources and required parameters, including the sources of pending or future inputs.
- **Sequence and dependencies:** Execution order and dependencies, plus layout or part relationships when assembly is needed.
- **Delivery:** Models, file formats, and any assembled files to provide.

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
