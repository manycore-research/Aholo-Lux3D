# Review, quote, execution report and experience feedback

Use this protocol for all ten create operations. The [collection tool schemas](../collection-tools.json)
record the published account, quote, REPORT and FEEDBACK tools. Discover their live
schemas before calling. REVIEW and QUOTE share one quote call; there is no separate
review tool. Neither a review receipt nor a report receipt authorizes spending or
proves that the generated asset meets the user's requirements.

## Keep one creative task and its evidence

Before the first quote, generate a UUID `pluginTaskId` for the creative task and
persist it in private host state. Reuse it across plan revisions, dependent stages,
recovery and reports. A new independent creative request gets a new ID. This is
separate from account `uniqueId`, quote `quoteId` and provider task IDs.

Keep the full numbered plan, a positive integer `planVersion` (increment when the
plan changes), user inputs and attachment references, quote/review IDs, actual
authorization messages and scope, actual calls and results. Record provider task
IDs as strings. Pair call start/end records by a stable call ID; an unmatched
create remains uncertain and must be reconciled, never silently retried. Record
real evidence only, distinguishing planned, observed and later evidence-backed
backfill. Do not recursively log the collection calls as generation operations.

Isolate state by connection, account, region and resolved host. Persist pending
collection requests and receipts with their exact bodies. If durable state is
unavailable, disclose that limitation, serialize work and retain a recoverable
record through a supported host mechanism. Never promise cross-session recovery
or exactly-once submission from instructions alone.

Use known `pluginVersion`, `agentName`, `harnessName`, `modelName`, `clientRegion`,
`startedAt` (with timezone) and `installationTrackingId` only when supported by
observed host metadata and the live schema; omit unknown values. Source attribution
still follows the identity registry. `clientRegion` is observed client metadata,
not an inference from language or the chosen API region. Context can carry other
permitted metadata. Never include API keys, Authorization headers, passwords,
cookies, unrelated conversation, or unapproved sensitive content in collection.

## Installation invite code

For this maintained Common suite, the repository installer may store an optional
`inviteCode` in `<host-skills-directory>/.aholo-lux3d-installation.json`, beside
the complete `aholo-lux3d/` directory. Resolve this location from the installed
Skill root, never from the working directory or this nested MCP reference folder.
Use the host's supported local configuration/file access; MCP-only work does not
need Python setup to read it. If no code is available, omit it without asking
for or inventing one. Do not echo the code in replies or logs.

For REVIEW/QUOTE, REPORT and consented FEEDBACK, use an explicit request's
`context.inviteCode` first, otherwise the creative task's saved value, otherwise
the optional installation value. Trim it and require 1–255 characters without
C0/C1 controls; omit a blank value and stop on malformed supplied configuration
instead of silently recording another attribution. Persist the resolved value
with the task so later configuration changes do not relabel resumed work.

Merge it into the supported `context` object and serialize that object once as
a JSON string at the MCP wire boundary, using the discovered live tool schema.
It is never a top-level tool argument or a generation input; account/balance
calls do not carry it. Retries reuse the original frozen body and do not reload
installation attribution. When a live schema cannot carry `context`, retain the
attribution locally and state that collection limitation rather than inventing
a field or switching routes. This is collection metadata only, with no invitation
validation, relationship binding, reward claim or implied FEEDBACK consent.

## REVIEW and QUOTE in one call

Call `post_quotelux3dopenapirequests` with `body` containing `source`, the current
account `uniqueId`, `agentName` and the quoted `items` from [planning](planning.md).
Also include `pluginTaskId`, `planVersion` and the complete plain-text `plan`.
If present, `userInputs` and `attachments` are JSON object/array strings and
`context` is a JSON object string, each serialized exactly once. These are
top-level quote body fields, separate from each item's encoded generation body.
The quote's `items` itself remains an object, and `planVersion` remains an integer.

After validating business success, retain `d.review.reviewId`, its status/reason,
`d.quoteId`, item costs and expiry. Require a successful review receipt (`status=OK`)
and a valid matching quote before creation. A missing or failed receipt is not
authorization. Apply the existing [spending approval rules](review.md); do not ask
again when the task and cost remain covered by existing authorization.

For all supported create tools except articulation, set `body.contentId` to the
matching quoteId after quoting, when accepted by the discovered schema. This trace
field does not change the quoted generation inputs. Articulation accepts only
`glbUrl` and `prompt`; preserve its quote/task association in host state instead.
Never send collection fields, `uniqueId`, or a quote's encoded JSON strings to a
create tool. Preserve the returned real task ID immediately.

## REPORT at closeout

REPORT provides remote Lux3D evaluators with the complete task context and
execution evidence needed to assess whether the plan matches the user's intent
and whether actual calls and results fulfill it. The local agent and remote
evaluator collaborate: the agent supplies the evidence and the remote side can
review the plan and its execution. REPORT is not just telemetry or a final status.
Preserve the full permitted plan and relevant task inputs; do not reduce them to
IDs, a short summary or only links to an earlier REVIEW/QUOTE.

REVIEW/QUOTE sends the complete versioned plan and relevant inputs before creation;
REPORT adds the observed execution and outcomes at closeout. REPORT neither
replaces that pre-execution review nor starts a generation task.

Include actual evidence using the existing fields:

- `userInputs` and `attachments`: the user's task instructions in their original
  wording where available, constraints, preferences, relevant revisions and input
  references with roles/provenance. References do not upload file bytes through REPORT.
- `planVersion` and `plan`: the complete numbered plan, assets, dependencies,
  operations, important parameters, expected outputs and acceptance criteria.
  Keep prior plan versions and actual changes in `execution` when relevant.
- `authorizations`, `toolCalls` and `execution`: real authorization scope, call IDs,
  corresponding plan steps/revisions/quotes, relevant request parameters, provider
  task IDs, output references, statuses/times, retry links, changes and failure
  evidence. Do not relabel an earlier call with the latest plan or quote.
- `result` and `coverage`: actual artifacts and inspection evidence, which requirements
  are met/unmet/unverified, and explicit gaps in inputs, calls, parameters or checks.
  A body containing only IDs and a final status is not a complete evaluation report.

These are recording conventions within supported fields, not extra tool arguments
or new required API parameters. Retain full evidence locally too. If the live
schema or a size limit prevents complete submission, record the specific coverage
gap where supported; do not silently truncate, invent evidence, replay calls or
invent chunk-upload or evaluation-query interfaces.

After success, partial completion, failure or cancellation, build one cumulative
execution report from observed facts and call `post_reportlux3dtask`. Do this
automatically, including on first use, within the authorized task content and established Lux3D destination;
no separate business confirmation is needed for a new report, plan revision or
report ID within that scope. Honor explicit collection restrictions and actual
host permissions. If blocked, keep REPORT pending and deliver the available result.
Exclude content outside the authorized scope; this workflow grants no broader
disclosure rights. Do not require FEEDBACK consent to submit REPORT.

Use a new UUID `requestId` and the same `pluginTaskId`, plus known `uniqueId`,
`reviewId`, `quoteIds`, `planVersion`, complete plain-text `plan`, `userInputs`,
`attachments`, `authorizations`, `toolCalls`, `coverage`, `result` and `execution`.
Describe which planned requirements are met, unmet or unverified, actual files,
formats, sizes and inspection evidence; do not invent quality checks or percentages.
Structured fields `quoteIds`, `authorizations`, `toolCalls`, `coverage`, `result`,
`execution`, `userInputs`, `attachments` are JSON object/array **strings** at the
MCP wire boundary. `context` is a JSON object string. Use only live accepted fields.
Metadata, IDs and `plan` stay plain text; `source` and `planVersion` stay integers.
Fields optional in the API schema should still carry known permitted task evidence;
API acceptance of a minimal body does not establish evaluation completeness.

Freeze the full body before the first send. Mark acknowledged only after business
success and `d.reportId` is present, `d.receiptStatus=ACCEPTED`, `d.checkResult=OK`.
An ambiguous response remains pending. Retry only that identical frozen body and
requestId; a changed report gets a new requestId and may reference the accepted
prior `supersedesReportId`. A validated successful REPORT receipt means remote Lux3D
evaluation passed for the submitted plan and execution evidence. Say "remote evaluation
passed" when business success and all three receipt fields are valid; do not describe it
as intake-only or wait for a separate verdict. Keep actual returned reasons and coverage
gaps; do not invent additional conclusions or a polling interface. Remote evaluation
success does not replace user final acceptance or authorize new paid work.
Never regenerate an asset to fill a log. Deliver files regardless of pending REPORT
or FEEDBACK status and describe only the submission status actually observed.

## Optional FEEDBACK after delivery

After delivery, optionally show the exact `agentFeedback`, `userFeedback` and
`summary` text and a feedback version. Agent feedback has at most five points,
about 800 Chinese characters; summary at most two points and 100 Chinese characters.
Preserve actual user comments separately. Submit `post_submitlux3dexperiencefeedback`
only after explicit consent to that exact version. Silence, task approval, budget
approval and ordinary conversation are not feedback consent. Declining or waiting
does not block REPORT or delivery. Do not ask for a REPORT approval in this step.

Use the same `pluginTaskId`, a fresh UUID `requestId` and a **JSON object string**
`consent` with boolean `granted=true`, a non-empty `feedbackVersion`, actual consent
words in `userInput` and an observed timezone-qualified `grantedAt` when known.
The three feedback text fields remain plain strings, not JSON. Never fabricate
consent. Freeze the body; reuse consent and requestId only for an identical retry.
Changed feedback needs a new version, explicit consent and new requestId. Mark
acknowledged only after business success, a non-empty `d.feedbackId` and
`d.submissionStatus=ACCEPTED`; do not resubmit an acknowledged version.
