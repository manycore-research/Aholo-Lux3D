# Execution and recovery

Choose the interface needed for the current action. Read the command's `--help` for arguments and the contracts below for request, response, and state structures.

## Use capabilities as needed

### Before calling a Lux3D API

Let the user choose the region; do not infer it automatically. Ask if no region has been selected, or reuse an explicit choice. Before the call, load the saved configuration for that region into the tool process. The tool reads the API key and authenticates through the actual request. If credentials are missing or invalid, follow the setup flow below. Conversation and local operations do not require an authentication check. A network or service failure does not mean the key is invalid.

### Set up an API key

1. Use an available single-choice interaction to ask, "Do you use the China site (.cn) or the international site (.com)?" Do not repeat the question if the region is already clear in this setup flow.
2. Provide the [China API key page](https://labs.aholo3d.cn/api-keys) or [international API key page](https://labs.aholo3d.com/api-keys), according to the user's choice. Say, "Create an API key here, then send it to me and I'll configure it for you." Wait for the key.
3. Once the key arrives, use local file and command capabilities to save the configuration and load it into the tool process that will make the call. The user should not need to set environment variables manually.
4. Verify the configuration with the `balance` command below. On success, briefly confirm setup and resume the original action. For an authentication failure, ask the user to check the region and key. Treat network failures as service issues.

| Region | Environment variable | Top-up / upgrade |
| --- | --- | --- |
| `cn` | `LUX3D_CN_API_KEY` | [Plans and credits](https://www.aholo3d.cn/pricing) |
| `international` | `LUX3D_GLOBAL_API_KEY` | [Plans and credits](https://www.aholo3d.com/pricing) |

Save the configuration in the user's private `~/.config/lux3d/credentials.json` file. Store the selected region in `region`, and keep keys under `apiKeys`, indexed by `cn` and `international`. Update only the selected region's key. Restrict access to the current user and keep the file out of projects and version control. Do not echo the received key in replies, logs, command-line arguments, quote files, or delivery files.

Each time a tool needs the Lux3D API, read the latest configuration as data, inject the selected key into the corresponding environment variable above, and pass the region explicitly. Existing host environment configuration may also be used, but a newly saved or updated key must replace the old value in the current tool process. Tools currently read environment variables; they do not read this configuration file themselves. Load the configuration as part of the local invocation, without relying on refreshed chat context or an `export` in another terminal.

Account setup and queries must not create or modify files in the user's project. Save credentials only in the private configuration file above; reading existing configuration and passing it to a tool does not require a persistent helper script. Use a one-off command to load the configuration and invoke the tool. If a temporary script is necessary, put it in the system temporary directory, keep credentials out of its source, and remove it after use.

If the user has not supplied a key or verification has not succeeded, preserve the request and pause API-dependent actions. When resuming, continue to follow the rules for querying original tasks, verifying uncertain submissions, and obtaining approval for charges.

### Query or refresh the account

Use `balance` in `scripts/commerce.py` to query balance, trial access, and membership entitlements, or to verify setup and account changes after a top-up. See `core/contracts/lux3d-commerce.v1.json` for responses and errors. Quoting already refreshes the account, so a separate balance query is not needed before every API call.

If balance or required entitlements are insufficient, help the user address the issue and query again before resuming. Do not require an upgrade for optional concurrency. After switching accounts, refresh quotes using [Understanding and planning](planning.md).

Use the returned `accountRef`, `region`, `source`, `uniqueId`, and `uniqueIdExpiresAt` to associate account facts with a quote. If a balance refresh changes `uniqueId` or the account, the earlier quote no longer applies: quote the intended work again. Do not invent membership requirements from `memberType` or trial names; enforce only requirements documented for the selected capability or returned by the service.

### Submit or resume a generation step

Use the bundled Python API in `core/runtime/lux3d_client.py`. With the configured Python interpreter, add the installed Skill's `core/runtime` directory to the process's import path and import `lux3d_client`. Pass the selected `region` and the approved parameters explicitly. Read the selected function's signature and `core/contracts/lux3d-generation.v1.json` for arguments and output formats.

| Operation | Submission function |
| --- | --- |
| Text to 3D | `create_text_to_3d_task` |
| Image(s) to 3D | `create_image_to_3d_task` |
| Material transfer | `create_material_transfer_task` |
| Four-view generation | `create_image_to_four_view_task` |
| Format conversion | `create_multi_format_export_task` |

These functions submit one task and return its ID. Use them separately from polling so the ID can be saved immediately. They do not check user approval or manage the plan's budget. The agent performs the following steps:

1. Check that the current step still satisfies the agreed constraints in the plan, and that its inputs and dependencies are ready. Inspect generated four-view inputs using the check below before submitting them to 3D generation. Match the actual operation, model, parameters, quantity, account, and region to a successful, unexpired quote from `scripts/commerce.py quote`. Requote changed or expired work and apply [Review and approval](review.md), including the remaining cumulative conversation allowance and any new retry costs. Check the account facts and required entitlements; refresh stale facts before submission.
2. Use the attempt record and recovery rules below to establish that this step has not already been submitted. Keep one submitting process per attempt.
3. Before making the call, save a local attempt record with the region, a non-secret account reference, the operation and approved parameter snapshot, quote/approval references, retry count, and submission start time. If a conversation budget is active, reserve the quoted allowance through the task's single budget coordinator and associate it with this attempt. Reuse an existing batch reservation rather than count the same amount again. Immediately before dispatch, mark submission as started and move the reservation to committed allowance. Keep temporary input URLs in private working files; do not copy credentials or signed URLs into portable records.
4. Call the selected `create_*_task` function once. Immediately save its returned ID to the attempt record and budget ledger before polling or doing other work. If the call times out, its result cannot be parsed, or saving the ID fails, preserve all available evidence and treat the outcome as uncertain. Keep its allowance committed; do not rerun the create call or assume a refund to recover it.
5. Query the saved ID until it reaches a terminal state, updating the record with actual status and timestamps. Download and inspect successful outputs, then follow [Results and delivery](results.md). A tracking interruption resumes from the saved ID.

This is agent orchestration using existing client functions, not a runtime-enforced approval, budget, or idempotency guarantee. Do not route this path through `workflow_runner.py run` or `resume`: its default CLI does not supply the required execution adapters. Their absence does not make the client functions unavailable. An actual authentication, entitlement, permission, or service rejection must still be handled; do not change accounts or endpoints to evade it.

The full `lux3d-workflow/v2` execution contract describes the runner's verification, gate and registry ports. Direct client orchestration does not implement those ports. Do not fabricate their decisions or describe a local delivery snapshot as compliance with that execution contract.

### Keep records and resume at the unfinished stage

Keep one task-local record per generation attempt and update it as facts arrive, rather than reconstructing submission history from separate scripts. It holds the stable item/attempt IDs, account/region, operation and parameter snapshot, quote/approval references, retry count, submission state, returned task ID, provider status, timestamps, and downloaded file paths. Keep private request inputs separate from portable delivery data. Budget amounts and reservation rules belong to the ledger in [Review and approval](review.md); refer to its entries rather than maintain another total.

On interruption or context compression, retain the record locations, current stage, unfinished items, and next action, plus the budget ledger location and totals if active. Resume according to the recorded facts:

| Known state | Next action |
| --- | --- |
| No submission started | Check current inputs, quote, and approval before submitting. |
| Submission started, outcome uncertain | Reconcile the original call; if unresolved, pause that step without another create call. |
| Task ID saved | Query that ID with its recorded account and region. |
| Generation succeeded, files missing | Download and inspect the original outputs. |
| Models ready, Blender work unfinished | Resume from the saved scene/script and completed renders using [Scene assembly and rendering](assembly.md). |
| Outputs ready, packaging or preview failed | Repair delivery using [Results and delivery](results.md). |

Keep generation, download, Blender, and packaging progress distinct. A later-stage failure does not erase an earlier success. Derive the delivery snapshot from these records as described in results; it is not a second execution log or authorization record.

### Query tasks or find records

Use `query` in `core/runtime/lux3d_client.py` to check the original task, or `list` to find generation records. The corresponding Python functions are `get_task` and `list_tasks`. Read `--help` or the function signature for arguments and `core/contracts/lux3d-generation.v1.json` for statuses and errors. Use query results to establish the actual state; a similar description alone does not identify the same task. Query with the recorded account and region. Resume from that record, without submitting again. If an uncertain submission cannot be conclusively matched to a task, pause that step.

### Read and download successful outputs

Use the existing output helpers in `lux3d_client.py`; do not guess formats from URL suffixes or drop empty result slots before interpreting them.

- Text/image to 3D: determine `expectedFormats` with `generation_result_formats(version, outputFormat)` and parse a successful task with `parse_task_outputs`.
- Material transfer: use `material_result_formats(outputFormat)` and `parse_fixed_output_slots(task_data, MATERIAL_OUTPUT_SLOTS)`.
- Format conversion: use `export_result_formats(modelUrl, outputFormat)` and `parse_fixed_output_slots(task_data, EXPORT_OUTPUT_SLOTS)`.
- Four-view generation: use `parse_task_outputs` and require the documented four URLs. When used for 3D generation, retain their documented order and inspect consistency before proceeding. If the user requested the images themselves, download and deliver them directly as described in results.

For model outputs, `download_requested_models(outputs, output_path, expected_formats)` downloads the requested formats. Its return value is a list of `(path, byte_count)` pairs, not workflow state. Build delivery records from those real files. A saved task may also be polled/downloaded with `complete_task`, supplying the matching `expected_formats` and, for material/export, `output_slots`. Never use a `generate_*` convenience function to resume; it creates a new task before polling.

### Change or cancel running work

Query the original task first, then use only the modification or cancellation interfaces actually exposed. Update unsubmitted work through [Understanding and planning](planning.md). If the user asks to stop, stop further submissions and accurately report any work still running. A cancellation request does not establish successful cancellation or a refund.

The bundled client currently exposes no cancellation or in-place task modification command. Do not invent one. Without another verified interface, stop unsubmitted work and explain that an already submitted task may continue.

## Inspect visual inputs and correct mismatches

Before using generated four-view images, inspect them together with the original reference. Check that they describe the same object with consistent structure and asymmetric landmarks such as openings, stairs, or a porch. Distinguish an expected change of viewpoint from genuinely mirrored or contradictory geometry. A successful image-generation task alone does not establish input consistency. Preserve the documented view order; arbitrary reordering is not a repair for conflicting views.

If a view is inconsistent, use a supported operation to regenerate the affected view, or regenerate the set if individual correction is unavailable. Inspect the replacement before use. If consistency still cannot be established, consider single-image generation from the original asset reference, provided the user's requirements permit it; explain a material route change. Do not repeatedly generate 3D from known conflicting inputs or mirror the finished model merely to disguise a mismatch.

Inspect successful 3D outputs against the agreed structure, orientation, silhouette, and material requirements before relying on them for assembly or declaring completion. For a concrete visual mismatch, identify whether the input, generation route, or local assembly needs correction. A justified new generation is production revision, not recovery from a download or preview failure. Quote its cost and apply the existing approval mode and remaining budget before submission. For either inconsistent four-view images or a mismatched 3D model, make at most one automatic corrective regeneration for the same mismatch by default. If it persists, revise the approach or report the limitation rather than loop; renaming the mismatch or changing attempt IDs does not reset this limit. A user explicitly requesting further candidates may authorize a larger bounded search. Preserve previous usable outputs and stop when the requirement is met or the authorized allowance is insufficient.

## Execution rules

- Before every new billable submission, including a retry, apply [Review and approval](review.md). Automatic execution uses the cumulative conversation budget. Each new retry has its own allowance entry; query retries keep the original task and do not consume additional generation allowance. Do not reset usage when the plan, attempt ID or context changes.
- Keep querying the original ID for an existing task. Successful submission does not mean generation is complete. If a query fails or the tracking window ends, preserve the last known state. Do not regenerate, report generation failure, or promise background tracking that is not available.
- Verify an uncertain submission result before proceeding. If it cannot be verified, pause that attempt and its dependent work instead of resubmitting. Independent work may continue only when its inputs, authorization, and budget remain established, with the uncertain amount still committed.
- After a confirmed generation failure, automatically resubmit the original step at most once, only if the failure is suitable for retry and the cost has the required approval. A new task ID does not reset this limit. Stop after another failure.
- If generation succeeds but downloading, opening files for inspection, or previewing fails, recover that local stage using [Results and delivery](results.md), without regenerating. A successfully inspected model that visibly misses agreed requirements follows the visual-correction rules above; a user-requested appearance change follows [Understanding and planning](planning.md).
