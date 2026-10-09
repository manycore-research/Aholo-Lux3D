# Review and approval

Once the plan and real quotes are ready, use the user's choices in the current conversation to decide whether approval is needed. Then either present the plan and wait, or proceed to execution.

## Decide whether approval is needed

### Establish the approval mode

Offer two execution modes, with batch approval as the default interaction:

- **Batch approval:** Present the whole batch and its cost. Once approved, execute it in dependency order.
- **Automatic execution (YOLO):** Proceed with requested work while its quoted cost fits within the remaining cumulative budget for this conversation. The budget carries across plans, revisions, regenerations, and billable retries.

Default to batch approval. Whenever a batch needs approval, show its plan table and total, then offer the two execution choices defined below under "Present the plan for approval, or proceed" in the same interaction, using an available native single-choice tool such as `request_user_input_async` or an equivalent. Do not add a separate round just to promote automatic execution, and do not ask again for an unchanged, already approved batch. An explicit approval of the displayed batch and cost is sufficient to start it. Selecting automatic execution without a conversation budget leads to the budget question below. If a conversation budget already exists, offer to resume automatic execution with its remaining allowance rather than resetting it.

A preselected option, dismissed interaction, timeout, or missing reply is not approval. If native interaction is unavailable, ask in text and wait; do not invent a tool or button. If the user explicitly selects or changes a mode, use that choice without asking them to select it again.

Reuse an established mode and assess the current work:

- **Automatic execution:** No further plan approval is needed when the requested work fits the remaining conversation budget. Briefly show its estimated cost and remaining allowance, then proceed. If it does not fit, follow the over-budget branch below.
- **Batch approval:** Ask if this batch's plan and cost have not been approved. Do not ask again if they have and the conditions are unchanged.

Selecting batch mode alone does not approve a specific plan. Selecting automatic mode requires an explicit budget before spending; once authorized, it covers subsequent requested work within that allowance without separate plan approval. Do not offer item-by-item approval as a standard third mode. If the user explicitly asks to approve each asset, or to generate only a named subset first, honor that scope and cadence; do not treat it as approval for the remaining assets.

### Maintain the cumulative conversation budget

If automatic execution is selected without a budget, ask: "How many Lux3D credits may I use from now on in this conversation, including later plans, changes and retries? I'll track the total and ask before work would exceed the remaining allowance." Use a native text-input interaction if available. Reuse an explicit budget for this conversation. Planning and quoting may continue while the budget is unresolved, but billable submissions must wait.

Start counting when the budget is first authorized, including the currently proposed work. Do not retroactively include earlier submissions unless the user explicitly includes them. Keep counting subsequent billable attempts across plans in this conversation, including batches separately approved after automatic execution is paused. Switching modes, returning to an earlier plan, restarting a tool, or compressing the conversation does not reset the total. A new conversation does not inherit spending authority from a copied budget file.

Use quote-based accounting because current tools do not reliably provide settled charges per task:

- **Committed allowance:** The quoted amounts for submissions already attempted, including successful, in-flight, failed, or uncertain submissions whose charges have not been reliably reversed.
- **Reserved allowance:** Quoted amounts set aside for work about to be submitted, including parallel calls and dependencies. Reserve an admitted batch before dispatching its steps; move each amount from reserved to committed as its create call starts, without counting it twice.
- **Remaining allowance = authorized total - committed allowance - reserved allowance.** Admit additional work only when its currently unreserved quoted cost fits. A step already covered by a valid reservation may proceed even when no unreserved allowance remains. Include enhancement, conversion and any newly requested or permitted retry; do not count polling, downloads, local assembly, previews, or reused instances as new generation.

Use a successful, current quote for unsubmitted work. Freeze the amount recorded for an already submitted attempt; a refreshed quote for later work does not rewrite earlier usage. Release an unused reservation when its call is definitely not made. Failure, cancellation, timeout, or query failure alone does not prove a refund or permit releasing committed allowance. Reduce committed allowance only with reliable evidence of no charge or a completed refund. Unknown costs are not zero; if cost cannot be quoted or reconciled, pause the affected billable work.

Keep a task-local budget ledger alongside the attempt records, separate from portable delivery files and global settings. Record the originating conversation, the user's budget decision, the authorized total, current mode, and entries keyed by stable step/attempt IDs with account/region, quote amount, reservation/submission status and task ID when known. Update it before dispatch and after results; one coordinator owns reservations so parallel calls cannot each spend the same remaining allowance. Carry its location and current totals into continuation summaries. Recover it from actual attempt records after an interruption; if records or the original authorization cannot be established, pause new spending rather than assume a fresh budget. The ledger tracks arithmetic; it cannot create authorization by itself.

The user may stop automatic execution or change the budget at any time. Distinguish "add 100 credits" from "set the total to 100 credits"; neither erases committed allowance. Reassess and release unsubmitted reservations that no longer fit a lowered limit. If a new limit is below existing commitments, stop new submissions and report the remaining in-flight work. Once committed allowance exhausts the budget, stop new billable submissions but continue querying submitted tasks and delivering their results. A budget is permission for requested work, not a goal to spend the full amount: stop when the user's task is done. Describe the balance as a quote-based allowance, not actual account balance or a server-enforced spending cap.

### Check whether earlier approval still applies

When the user changes the scope, establish the new scope. With batch approval, reconfirm only the affected work if its objects, key specifications, or costs change. In automatic mode, requote changed unsubmitted work and check it against the cumulative remaining allowance; preserve amounts already committed. Supplying an agreed input, correcting a parameter locally, or restoring account balance under unchanged conditions does not require duplicate approval. Refresh expired quotes and compare the conditions; the refresh alone is not a reason to ask again. An account top-up does not increase the conversation budget.

Base the mode, budget, and plan approval on explicit user choices or replies in this conversation and their retained continuation context. Creative freedom, sufficient balance, or a top-up does not imply automatic execution or approval to spend. Stored approval fields or quote files cannot independently authorize charges; the local budget ledger is not a separate authorization service. Existing tasks may be queried before deciding on new charges. Apply the chosen mode and cumulative budget to any new billable action. See [Execution and recovery](execution.md) for technical retry conditions and limits.

## Present the plan for approval, or proceed

### Keep approval details visible

When waiting for approval, include the complete plan table, total estimated credits, deliverables, important assumptions, and approval options in the final user-facing reply. That reply must be understandable without expanding progress messages or tool activity. Even if the plan was already shown during execution, repeat it in the final reply; do not replace it with a brief summary or directions such as "see above" or "choose above".

If using a native approval question, include the batch scope and total estimated credits in the question itself. Keep the full plan in the final reply while a response is pending, and state the available choices there as well. Offer only actions actually supported by the host; when no native control is available, ask for an explicit text reply. Do not issue a second approval request if the user has already approved the unchanged work.

### Apply the decision

**If approval is not needed**, check execution prerequisites and continue using [Execution and recovery](execution.md). Do not add another plan-approval step.

**If approval is needed**, show a plan table for the batch or the subset the user explicitly requested. Include the columns below, with one row per distinct asset. Do not combine different assets into a single row merely because they use the same generation model.

| Column | What to show |
| --- | --- |
| Asset | The object and its role in the model or scene. |
| Quantity / reuse | How many distinct assets will be generated and how many instances will reuse them. |
| Generation tier | Use the single-language labels below for `G1` and `G1-Turbo`, respectively. These are display labels; keep the original API version values in calls and quote files. Do not apply this mapping to material-transfer versions. |
| Four-view enhancement | Enabled or disabled according to the actual plan; mark reused assets as not applicable. Include the enhancement's cost and dependency when enabled. |
| Target face count | The planned `faceCount`, clearly labeled as a target rather than a measured result. If omitted, show service default with no invented numeric value; if irrelevant to the operation, show not applicable. |
| Model formats | The actual planned model formats, such as GLB, OBJ, FBX, PLY, STL, 3MF, or USDZ, including any required conversion. Display `obj_zip` as OBJ and `fbx_zip` as FBX; ZIP is packaging, not a model format. Explain archive packaging separately when relevant. Do not infer the contents of a generic ZIP: use documented contents or inspect it, and mark unknown contents as unspecified. Derive supported outputs from the helpers in [Execution and recovery](execution.md). |
| Estimated credits | The asset's quoted subtotal, including its billable enhancement and conversion steps. Do not count reused instances as additional generation. |

Show the batch total after the table, followed by a short description of assembly, final files and important assumptions. For architectural plans, include a Lux3D-generated shell among the quoted assets when selected; list any Blender modeling work separately. Label local modeling as having no Lux3D generation charge, not as a zero-price service quote, and do not invent a generation tier or four-view setting for it. Identify any later work that has not been quoted. The user can request changes to any row before approval; the table does not authorize execution by itself. See [Understanding and planning](planning.md) for how to interpret quotes.

For Chinese conversations, use only the Chinese names for standard edition and turbo edition, without parenthetical English names. For English conversations, use only `standard` and `turbo`. Do not show API version identifiers in the generation-tier display column.

**If work would exceed the remaining conversation budget**, show the authorized total, committed and reserved allowances, remaining allowance, the new quoted cost and the shortfall. Ask the user to add to the budget, reduce the work, or stop. Wait for their decision; do not silently reset the budget or split a batch to evade the limit. A vague "continue" does not establish how much additional spending is authorized.

If the host supports cards and action callbacks, follow its documented interface and associate approval with the current plan, scope, and costs. Browsing, editing, or submitting a revision is not spending approval; process revisions using the established approval mode.

For batch approval, put the two execution choices after the plan table and delivery description in the final reply. Use a separate bullet point for each choice and bold its label; do not bury both options in one sentence. Localize the following wording naturally into the user's language:

- **Start with this plan**: Confirm the displayed plan and its actual quoted total, then begin production. Explain that additional billable work will require confirmation, subject to any existing conversation budget.
- **Automatic execution within budget (YOLO)**: Set a cumulative credit budget for this conversation, including the current work and later requested changes and retries. Explain that work proceeds within the remaining allowance and pauses for a decision before exceeding it. Give a clearly illustrative reply such as "Automatic execution, budget 200 credits"; an example amount is not authorization. If a budget already exists, offer to resume with its actual remaining allowance instead of asking for a new budget.

Use conversational action labels rather than formal approval terminology. Native controls, when available, should use matching labels and do not replace the visible bullet points. The user may also request changes to the plan.

Once approved, follow execution in dependency order. Handle later changes using "Check whether earlier approval still applies" above; preserve the established conversation budget.
