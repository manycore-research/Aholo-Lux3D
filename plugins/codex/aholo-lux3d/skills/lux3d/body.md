# Lux3D

Use the current request, conversation, and execution results to decide which stage is ready to proceed. Address missing prerequisites without restarting the whole workflow. Wait when user input or approval is required. Read references as needed; reuse instructions already in context when they still apply.

## Workflow and prerequisites

### Understand the request and make a plan

Read [Understanding and planning](references/planning.md) when a creation or revision request needs an executable plan. Use the request, existing models, and available capabilities to fill in reasonable details or ask for essential information. Choose the production approach, prepare and validate parameters, and obtain cost estimates. Once the plan is executable and the relevant costs are known, follow the selected approval mode.

If only an agreed input is missing or a parameter needs correction, keep the plan and address that gap. Answer ordinary conversation directly. When the available information already supports approval, a status query, or delivery, proceed with that action.

### Apply the approval mode

Once there is an executable plan and a real quote for the relevant work, read [Review and approval](references/review.md). Default to batch approval: show the detailed plan table and offer approval of that batch or a switch to automatic execution (YOLO) in the same interaction. Automatic execution requires an explicit cumulative budget for this conversation. Carry its remaining allowance across plans, revisions, retries and context compression; use the budget ledger and prior approval to decide whether work may proceed.

When no further approval is needed, briefly report the new work's estimated cost and remaining allowance, then check execution prerequisites. Otherwise, present the batch's plan and costs, or only the subset explicitly requested by the user, then wait. If work would exceed the remaining conversation budget, pause new submissions until the user adds budget or adjusts the work. After a requested change, update the plan and quote, then reassess. Budget exhaustion does not stop queries or delivery of already submitted work.

### Execute and track

Once the current step has the required approval, follow [Execution and recovery](references/execution.md) to check actual inputs, parameters, dependencies, balance, and required entitlements. Submit and track the step when these checks pass. Fix input or parameter errors locally. If balance or entitlements are insufficient, help the user address the issue, then check again.

For an existing task, query that task and continue from its status; a new message does not require a new submission. Use the same reference for queries, recovery, changes to running tasks, and cancellation. When the required assets are ready, proceed to assembly if needed, or to inspection and delivery.

### Assemble models

Read [Model assembly](references/assembly.md) when the request involves a composed scene, a multipart model, or layout changes. Use an installed Blender executable through local commands, or an available Blender MCP. MCP is optional; a closed Blender window does not prevent background execution. If Blender is not installed and no usable remote Blender tool is available, ask whether the user wants help installing it. Once the required assets are ready, assemble, inspect, and deliver the result.

### Inspect and deliver

When model files are available for inspection, read [Results and delivery](references/results.md). Inspect the files, prepare a unified delivery bundle, and provide links or paths to the model files and `preview.html`. Do not open the preview automatically. Integrate the models into a downstream project only when requested. For partial success, identify what is available and what is missing. If no usable model is available and recovery is not possible, explain the failure and stop this attempt.

For requested revisions, identify the affected objects and scope, then continue at the appropriate stage. Reuse plans, approvals, and models that still apply.

## Rules throughout the workflow

- Use Lux3D capabilities for model, image, and material generation and processing. Use the tools specified in the relevant references for assembly, file inspection, and previews.
- Before calling a Lux3D API, load the configuration and authenticate as described in [Execution and recovery](references/execution.md). Follow its setup instructions if credentials are missing or invalid.
- Preserve original versions and unaffected models. Do not automatically score aesthetics or generate candidates to pick a winner. There is no fixed mid-execution image/model selection checkpoint.
- Never echo keys, tokens, or complete signed URLs. Keep accounts and tasks associated with their correct regions.
- Communicate in the user's language.
- Keep routine replies focused on the user's task: ask for needed information, present plans and costs, and report results directly. Avoid unsolicited process explanations, internal rule quotations, and recurring "this confirmation comes from" closing paragraphs unless the host explicitly requires them. Explain relevant reasons when the user asks, work fails or is blocked, or an important limitation affects their decision. Preserve required spending confirmations and permission disclosures.

## Command conventions

Tool paths in the references are relative to the directory containing the installed entrypoint `SKILL.md`. Run scripts with the Python interpreter configured for that environment. Read each command's `--help` for arguments and the linked contract for request-file structure.
