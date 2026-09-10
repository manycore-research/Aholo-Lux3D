# Review and approval

Once the plan and real quotes are ready, use the user's choices in the current conversation to decide whether approval is needed. Then either present the plan and wait, or proceed to execution.

## Decide whether approval is needed

### Establish the approval mode

Offer two execution modes, with batch approval as the default interaction:

- **Batch approval:** Present the whole batch and its cost. Once approved, execute it in dependency order.
- **Automatic execution (YOLO):** Proceed with requested work while its quoted cost fits within the remaining cumulative budget for this conversation. The budget carries across plans, revisions, regenerations, and billable retries.

Default to batch approval. Whenever a batch needs approval, show its plan table and total, then offer "Approve this batch" and "Switch to automatic execution and set a budget" in the same interaction, using an available native single-choice tool such as `request_user_input_async` or an equivalent. Do not add a separate round just to promote automatic execution, and do not ask again for an unchanged, already approved batch. An explicit approval of the displayed batch and cost is sufficient to start it. Selecting automatic execution without a conversation budget leads to the budget question below. If a conversation budget already exists, offer to resume automatic execution with its remaining allowance rather than resetting it.

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

**If approval is not needed**, check execution prerequisites and continue using [Execution and recovery](execution.md). Do not add another plan-approval step.

**If approval is needed**, show a plan table for the batch or the subset the user explicitly requested. Include the columns below, with one row per distinct asset. Do not combine different assets into a single row merely because they use the same generation model.

| Column | What to show |
| --- | --- |
| Asset | The object and its role in the model or scene. |
| Quantity / reuse | How many distinct assets will be generated and how many instances will reuse them. |
| Generation tier | Standard edition (Standard) for `G1`; Turbo edition (Turbo) for `G1-Turbo`. Localize the edition name into the user's language and retain the English name in parentheses. These are display labels; keep the original API version values in calls and quote files. Do not apply this mapping to material-transfer versions. |
| Four-view enhancement | Enabled or disabled according to the actual plan; mark reused assets as not applicable. Include the enhancement's cost and dependency when enabled. |
| Target face count | The planned `faceCount`, clearly labeled as a target rather than a measured result. If omitted, show service default with no invented numeric value; if irrelevant to the operation, show not applicable. |
| Model formats | The planned delivered formats, including any required conversion. Distinguish ZIP packages from individual GLB files; present `obj_zip` and `fbx_zip` as OBJ (ZIP) and FBX (ZIP). Derive actual outputs from the helpers in [Execution and recovery](execution.md). |
| Estimated credits | The asset's quoted subtotal, including its billable enhancement and conversion steps. Do not count reused instances as additional generation. |

Show the batch total after the table, followed by a short description of assembly, final files and important assumptions. Identify any later work that has not been quoted. The user can request changes to any row before approval; the table does not authorize execution by itself. See [Understanding and planning](planning.md) for how to interpret quotes.

For Chinese conversations, use the exact display labels `标准版（Standard）` and `极速版（Turbo）`. For English conversations, use Standard and Turbo.

**If work would exceed the remaining conversation budget**, show the authorized total, committed and reserved allowances, remaining allowance, the new quoted cost and the shortfall. Ask the user to add to the budget, reduce the work, or stop. Wait for their decision; do not silently reset the budget or split a batch to evade the limit. A vague "continue" does not establish how much additional spending is authorized.

If the host supports cards and returns user actions, organize cards by asset or production unit. Show the information above and allow the user to browse and request changes, following the host's interaction documentation. Proceed only after receiving the user's submitted approval or revision. Browsing cards or displaying an "Approved" label is not permission to execute. Returned actions must identify the current plan version, approved scope, and costs. Approval for an outdated plan cannot directly authorize a new one.

For batch approval, show the batch total, one "Approve entire batch" action and the alternative to switch to budgeted automatic execution after the table or cards. Browsing or editing a row or card does not start generation. Once approved, execute the batch in dependency order without asking for each asset again. Keep an already established conversation budget in force unless the user explicitly changes it.

If cards or action callbacks are unavailable, present the same information in text and obtain approval through a permitted native question tool or an explicit text reply. Wait after asking. Once approved, check execution prerequisites and continue. If the user requests changes, update the affected plan and quote, then reassess the selected mode. In batch mode, a revision request does not also approve the revised costs. In automatic mode, existing authorization covers the requested revision only when it fits the remaining cumulative allowance.
