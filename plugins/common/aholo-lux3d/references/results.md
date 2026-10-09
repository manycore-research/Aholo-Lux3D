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


## Plugin collection and feedback

Author: yinjie

Use one task journal per independent creative task. Keep it at the task output directory's
`logs/collection.sqlite`. Reuse it across plan revisions, retries and resumed conversations.
Never create a new journal merely to retry a failed upload. Account credentials stay in the
existing region-specific credential configuration, never in request files.

### Initialize and quote

Run `scripts/commerce.py init --region cn --journal <output>/logs/collection.sqlite`,
adding the known metadata arguments described below automatically.
Save the returned `pluginTaskId` in the task's continuation context. This command is local
and does not generate assets or call the balance API. It binds the task to the current
credential fingerprint, region, source and host; changing any of these cannot rebind it.

Prepare `review.json` with `pluginTaskId`, positive integer `planVersion`, the complete
textual `plan`, and optional `userInputs`, `attachments`, `context`. Structured fields may
be objects/arrays in the local file; the client serializes them to JSON strings on the wire.
Preserve original user input and plan text. Do not include credentials, hidden reasoning,
or unrelated conversation history. Context may contain `model`, `clientRegion`, plugin
version and installation tracking metadata when known; do not fabricate missing facts.

Run:

```text
scripts/commerce.py quote --region cn --items items.json --review review.json --journal <output>/logs/collection.sqlite
```

Retain the returned `account.uniqueId`, `quote.quoteId` and `quote.review.reviewId` with
the plan. A new quote creates separate REVIEW and QUOTE events. `review.status=OK` is a
collection receipt only; it is neither quality approval nor authorization to spend.
Unchanged legacy callers may still omit both `--review` and `--journal`; quote metadata
also works without them. The new plugin workflow still submits the complete review plan.

### Installation invite code

The Common local Skill installer accepts an optional code from the user's
`Invite Code:` installation request and stores it beside the Skill directory,
in `.aholo-lux3d-installation.json`, outside the verified package. Common loads
it automatically for `init`, `quote`, `report` and `feedback`; `balance` and
frozen retries do not read this configuration. Other integrations may explicitly
supply the same optional `context.inviteCode` in collection requests.

Use explicit request context first, otherwise the task journal's saved code,
otherwise installation configuration. Save the code with the task so a new
conversation or changed installation does not relabel previous work. Missing
codes stay absent. The field is a trimmed string of at most 255 characters with
no control characters; it is not `installationTrackingId`, a task ID or an API
key. Site retains it under `payload.request.context.inviteCode` in the existing
collection table. This is collection only, with no invitation validation,
relationship binding or rewards. Do not treat metadata as feedback consent.

### Collection metadata

The host agent must automatically include the actual model and client region when known,
without asking the user to configure an identity profile. At `init`, supply `--model-name`
from observable host session metadata and `--client-region` from an explicitly known
client location. Both arguments are also available on `quote`, `report` and `feedback`.
The task journal retains these metadata values for later events and resumed sessions.
When the current model or client location is observed to change, pass the updated value
on the next new event; do not relabel previously collected events.

```text
scripts/commerce.py init --region cn --journal <output>/logs/collection.sqlite --model-name <actual-host-model> --client-region <known-client-region>
```

The angle-bracket values are placeholders for facts the host can observe, never literal
values to send. Omit an argument if that fact is unknown; missing metadata must not block
work or prompt the user for setup. Integrations can supply `LUX3D_MODEL_NAME` and
`LUX3D_CLIENT_REGION` to the command process instead of flags. These are optional metadata
inputs, not required credentials or per-user binding files. Do not invent host-native
variables or scrape unrelated settings to fill them.

The model identifies the host agent's actual model, not the application name and not a
Lux3D generation version such as `G1`. Client region identifies the client's location,
not the API route `cn` / `international` or the Site deployment region. Do not infer
location from language, timezone, model provider or the selected API endpoint. Preserve
a genuine host-reported value; do not fabricate `unknown` or a plausible model name.

Review and quote send `context` as a JSON string with `model` and `clientRegion` when
known. Reports and feedback keep their supported top-level `modelName` / `clientRegion`
and the context values consistent. Site projects these values to `model_name` and
`client_region`; no new endpoint or database field is required. Unrelated context fields
remain intact. Empty or missing metadata does not overwrite a previously known value.
Precedence is explicit request data (top-level, then canonical context, then the
`context.modelName` alias), command arguments, integration environment, then saved
task metadata. If a reused request file contains an old model or location, update
that file for the new event too; a command argument does not override explicit
request content. Do not edit the frozen file when retrying an existing event.

`balance` does not collect these fields. `retry` accepts no metadata flags and reuses the
entire frozen request, even if the host model, environment variables or task metadata have
changed. A changed report or feedback payload is a new event with a new `requestId`, not
an amendment to the old retry.

### Generation correlation

Use the current quote's `quoteId` as optional generation `contentId`. The six shared
Python create helpers and generate convenience wrappers accept `content_id=quote_id`; wire requests use `contentId`. Existing create CLI commands accept `--content-id <quoteId>`. The active execution instruction requires passing the current matching quote explicitly.
The workflow generation-port request derives `contentId` from the verified submission's
`quoteId`. Keep generation parameters identical to the quoted parameters; correlation is
transport metadata added after pricing, not a creative input or authorization.
Do not substitute shared `uniqueId`, `pluginTaskId`, or provider task ID for this field.
Remote MCP tools must actually expose this input before using it; local support does not
prove a remote tool schema or gateway publication has been updated.

### Record as work happens

Follow the original PRD's recording requirements using the current runtime and host file tools. The journal freezes submissions; it does not automatically intercept host calls or build a complete report. Do not start the historical mock collector or invoke the old `collection.py` commands.

Keep task metadata and append-only execution records in the task directory's `logs/`. Retain original user inputs, input references and addedInVersion. Persist startedAt once: use the real task-start timestamp when observable, otherwise the initialization time with context.startedAtSource=`collection_init`; never manufacture an earlier timestamp. Known plugin version, host, model and installationTrackingId accompany requests through the supported context fields; unknown values stay unknown.

Record each real approval or approval-mode change with its original words, time, scope, explicit budget (otherwise null), authorizationId and supersedesAuthorizationId. Resuming unchanged authorization must not fabricate another confirmation. Review OK, quote success and recording an authorization do not create user consent.

For each observable task-relevant call not already captured by a reliable recorder:
1. Before execution append a start record with a fresh UUID callId, actual host tool name, operation, pluginTaskId, planVersion, time, screened input summary and applicable authorizationId/quoteId. Free local work has no fabricated quote. A confirmed retry uses a new callId and retryOf.
2. Invoke the actual tool normally. Recording is a side operation, not an execution proxy. Pass the current matching quoteId as content_id for every quoted Lux3D create.
3. Append the actual finish with the same callId and links captured at start, its status/time and observed output or error. Capture providerTaskId as soon as creation is accepted; acceptance is not completion. Polling is separate from creation and must not inflate generation counts.
4. After interruption retain unmatched starts and uncertain outcomes. Recover from actual task or host evidence, without repeating paid creates to fill missing logs.

Use the host's normal append/file facilities; no new recording CLI is implied. Do not log logger operations recursively. Distinct image-viewing calls remain distinct calls; a shell script's internal steps are not invented host invocations. Exclude routine Skill reads, but include task-changing edits, rendering and artifact inspection when observable. Do not record keys, hidden reasoning or unrelated conversation. Explicitly mark unavailable interception and failed writes as known coverage limitations.

### Task closeout order

<!-- Author: yinjie. Keep authorized factual reporting distinct from optional feedback. -->
Use this sequence for an authorized generation or revision task, including failure,
cancellation and partial delivery:

1. Reconcile observed execution facts and prepare REPORT within the task's already
   authorized collection content and established destination. Exclude credentials, hidden
   reasoning, unrelated conversation and sensitive content outside that authorization.
   This workflow does not grant broader disclosure rights. If scope or destination is
   unresolved, omit unapproved fields where valid or retain the report as pending.
2. Submit the permitted REPORT using the task's journal, account and selected region,
   and validate its receipt. Changed report content needs a new requestId; a retry uses
   the frozen request. These bookkeeping changes do not require a new report business
   confirmation. Honor an explicit collection restriction and actual host permission
   checks; if blocked, preserve the pending state and continue to delivery.
3. Deliver usable files and state material limitations. Receipt acceptance, feedback
   consent and user acceptance of the files are not prerequisites for delivery. Claim
   report submission only after validating its receipt; otherwise retain the pending data.
4. After delivery, optionally show the exact experience FEEDBACK text and version and ask
   whether to submit that feedback. Waiting for this answer, declining it or receiving
   no answer has no effect on REPORT. Do not return to step 2 to request business consent.
5. Submit FEEDBACK only with explicit consent to that exact version, using the normal
   host permission mechanism. Preserve the real consent words. Reuse unchanged consent
   for its frozen retry; changed feedback needs a new version and consent to that version.
   Do not repeat an already acknowledged submission.

### Execution report

The execution report is a core task-completion step for recording facts and assessing how
well the result meets the plan. Submit it automatically within the authorized task; do not
ask the user to approve each report, show an upload confirmation form, or wait for experience
feedback consent. This applies in both batch-approval and automatic-execution modes.
Actual host tool/network permission checks still apply. If those block submission, retain
the pending report and continue delivery; do not bypass restrictions. Honor an explicit
user instruction declining collection.

Within the existing authorization for the task's permitted report content and established
Lux3D destination, each report closes out the authorized work automatically. A new turn,
planVersion, report file, requestId or supersedesReportId does not by itself change that
scope or require another business-consent question. New paid work still follows the normal
generation approval rules. New sensitive content or a different destination is not covered
merely because the report has the same pluginTaskId; exclude unapproved content or preserve
it as pending rather than assuming consent. Preserve the actual task authorization history;
do not fabricate a report authorization or add a feedback consent field to REPORT.

Do not open a separate REPORT question/card, ask whether to upload it, or say earlier
agreement covered only the previous round as a reason to reconfirm unchanged report scope.
Feedback-version consent is only for FEEDBACK. An already established international route
is handled using the task's `international` region; the `/global` path itself does not create
another business-consent step or authorize changing destination.

Actual host tool, network and upload permissions are separate. Use the host's required
permission mechanism when it demands one, accurately describe the operation, and do not
add a duplicate conversational business-confirmation card. Do not bypass restrictions,
disguise REPORT as FEEDBACK, or promise that system permission dialogs will disappear.
If permission remains unavailable or denied, retain the pending report, deliver available
assets and state only the observed submission status.

After execution ends and before final delivery, including failure, cancellation or partial completion, prepare one cumulative
report from observed execution facts. Include `pluginTaskId`, a new UUID `requestId`,
optional `uniqueId`, `reviewId`, `quoteIds`, actual `authorizations`, `toolCalls`, `coverage`,
`result`, `execution`, and known metadata. Record provider task IDs as strings. Distinguish
planned actions from actual calls, and polling from paid creation. Mark missing evidence
as unknown. Reconcile providerTaskId, observed call pairs and actual artifact names/formats/sizes with the logs. Retain authorization history, plan revisions, retry and artifact provenance/replacement links. Evidence-backed backfill must be labeled as backfill, never represented as live logging. Do not calculate an unverified completeness percentage. Never regenerate assets just to fill an execution log.

```text
scripts/commerce.py report --region cn --request report.json --journal <output>/logs/collection.sqlite
```

In `result`, record which planned requirements are met, unmet or unverified, using the
actual files, task states and inspection evidence. Keep this factual assessment separate
from optional user satisfaction or experience feedback. Do not claim an unperformed visual
check or treat a receipt as proof that the user accepts the result.

The client freezes the full wire body before sending. It marks success only after validating
`reportId`, `receiptStatus=ACCEPTED`, `checkResult=OK`. This is not a quality assessment.
A revision gets a new `requestId` and may reference the prior `supersedesReportId`. These
identifiers track changed facts; they do not trigger another business-consent request
when the authorized content and destination remain within the established task scope.

### Experience feedback

After report closeout and delivery or explanation of the result, prepare `agentFeedback`, `userFeedback`, `summary` as plain text. Agent feedback is at most five points, about 800 Chinese characters; the summary is at most two points and 100 Chinese characters. Preserve user comments separately, without arbitrary truncation or replacing them with Agent opinions. Optional user questions: what was satisfying or unsatisfying about using Lux3D, and what capabilities would they like added? Answering these questions alone does not authorize sending. Show the exact feedback
and summary to the user and ask whether to submit that content. Submit only after explicit
agreement to this content version; silence, ordinary replies, task execution approval and
budget approval do not authorize feedback. Preserve the user's actual consent words.
`consent` is an object in a local file (or JSON string) containing boolean `granted=true`,
non-empty `feedbackVersion`, and when known `userInput` and `grantedAt`.
Include `pluginTaskId` and a fresh `requestId`. Changed feedback requires new consent,
a new feedback version and a new request ID.

```text
scripts/commerce.py feedback --region cn --request feedback.json --journal <output>/logs/collection.sqlite
```

A feedback consent question must identify experience feedback and show the exact
`agentFeedback`, `userFeedback` and `summary` to be shared. If using a question card, its
title, question and action labels must all describe that FEEDBACK version. Never label
it as permission to upload an execution report, bundle REPORT into this optional consent,
or ask for a broad permission covering both payloads.

No command manufactures consent. Feedback pending, refused or unanswered must not block
REPORT or delivery. A later turn alone does not invalidate explicit consent to an unchanged
feedback version; changed feedback needs its own new version and consent. Check `feedbackId`
and `submissionStatus=ACCEPTED` before saying it was submitted.

### Closeout examples

Author: yinjie

| Situation | Required action |
| --- | --- |
| An authorized task finishes on its already established international API route | Submit its permitted factual REPORT using `scripts/commerce.py report --region international --request report.json --journal <output>/logs/collection.sqlite`, validate the receipt, then deliver. No separate REPORT business question is needed; actual host permissions and the existing authorized data/destination scope still apply. |
| The user requests a revision and it proceeds under the applicable task approval | Submit the updated permitted cumulative REPORT with a new requestId and, when appropriate, supersedesReportId. A new round or identifier does not require duplicate report consent within the established scope. |
| REPORT is submitted; feedback v1 was approved, and v2 changes its text | Deliver the revision, show the exact v2 feedback, and ask only whether to submit that optional experience feedback. No answer leaves FEEDBACK v2 unsent; REPORT stays submitted. |
| REPORT is blocked by a real host network/upload permission | Use the required host permission mechanism without an additional report business-confirmation card. If blocked, retain the pending report and deliver; never wait for feedback consent as a substitute. |
| A proposed field or destination is outside the existing authorization | Remove the unapproved field if the remaining report is valid, or retain the report as pending and explain the limitation. Do not infer disclosure consent from generation approval, report IDs or silence. |

A feedback question can say: "Would you like me to submit the optional experience feedback
version v2 shown below?" For a supported question card, use "Experience feedback v2" as
the title and options such as "Submit this feedback" and "Do not submit feedback".
Localize them to the user's language and show the exact feedback with the question.
Do not use "Authorize upload of this execution report" for a feedback action. Example
wording does not itself provide consent or prove that any report was submitted.

### Recovery

If sending fails, continue delivering available assets and retain the pending journal.
Retry without reconstructing a body or generating a new ID:

```text
scripts/commerce.py retry --region cn --kind report --request-id <original-id> --journal <output>/logs/collection.sqlite
scripts/commerce.py retry --region cn --kind feedback --request-id <original-id> --journal <output>/logs/collection.sqlite
```

A malformed or unreadable request is `COLLECTION_REQUEST_INVALID`; fix the local input
without pretending it was submitted. `COLLECTION_JOURNAL_INVALID` indicates an unavailable,
conflicting or damaged journal: preserve it and its original request IDs, restore access
or a known-good copy, and retry the frozen request. Do not delete the journal, fabricate a
receipt, or create a new task/request ID just to hide the error. A report retry does not
require a new business approval; a feedback retry remains bound to its original consent.

Identical acknowledged submissions return their saved receipt. Changed body with the same
request ID is rejected locally; server `COLLECTION_EVENT_CONFLICT` is also surfaced. A
credential or region change prevents sending another account's pending data. Journals do
not grant spending permission. They contain collection content and belong with the task's
private output files, not in public delivery bundles or source control.
