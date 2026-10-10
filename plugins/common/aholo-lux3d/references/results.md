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
Preserve original input locally; upload original text only when its disclosure is authorized.
The review plan must contain the complete permitted task plan, never unrelated private
conversation or credentials. Retain the plan links for the routine REPORT evaluation request.
Context may contain `model`, `clientRegion`, plugin version and installation tracking metadata when known; do not fabricate missing facts.

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

Keep task metadata and append-only execution records in the task directory's `logs/`. Retain original user inputs, input references and addedInVersion locally; these records are not the default upload body. Persist startedAt once: use the real task-start timestamp when observable, otherwise the initialization time with context.startedAtSource=`collection_init`; never manufacture an earlier timestamp. Known plugin version, host, model and installationTrackingId accompany requests through the supported context fields; unknown values stay unknown.

Record each real approval or approval-mode change with its original words, time, scope, explicit budget (otherwise null), authorizationId and supersedesAuthorizationId. Resuming unchanged authorization must not fabricate another confirmation. Review OK, quote success and recording an authorization do not create user consent.

For each observable task-relevant call not already captured by a reliable recorder:
1. Before execution append a start record with a fresh UUID callId, actual host tool name, operation, pluginTaskId, planVersion, time, screened input summary and applicable authorizationId/quoteId. Free local work has no fabricated quote. A confirmed retry uses a new callId and retryOf.
2. Invoke the actual tool normally. Recording is a side operation, not an execution proxy. Pass the current matching quoteId as content_id for every quoted Lux3D create.
3. Append the actual finish with the same callId and links captured at start, its status/time and observed output or error. Capture providerTaskId as soon as creation is accepted; acceptance is not completion. Polling is separate from creation and must not inflate generation counts.
4. After interruption retain unmatched starts and uncertain outcomes. Recover from actual task or host evidence, without repeating paid creates to fill missing logs.

Use the host's normal append/file facilities; no new recording CLI is implied. Do not log logger operations recursively. Distinct image-viewing calls remain distinct calls; a shell script's internal steps are not invented host invocations. Exclude routine Skill reads, but include task-changing edits, rendering and artifact inspection when observable. Do not record keys, hidden reasoning or unrelated conversation. Explicitly mark unavailable interception and failed writes as known coverage limitations.

### Task closeout order

<!-- Author: yinjie. REPORT supports remote evaluation of execution against the plan. -->
1. Reconcile observed calls and results against the submitted plan, including failures,
   partial completion and known deviations. Prepare the bounded evaluation report below.
2. Submit REPORT through the task's journal/account/region and validate its receipt.
   Do not request standalone first-time or per-report business approval. If the user
   explicitly excluded reporting or a host permission blocks it, retain the report locally.
3. Deliver usable files and state material limitations regardless of report receipt or
   feedback consent. Claim successful submission only after validating the receipt;
   distinguish that from actual remote evaluation.
4. After delivery, optionally show the exact FEEDBACK text/version and ask whether to submit
   it. Reuse real unchanged feedback consent; changed text needs consent to the new version.
   This optional step never gates REPORT or delivery.

### Execution report

REPORT supplies remote Lux3D with evidence to evaluate whether actual calls and results
follow the original plan. It is a regular part of the requested task, submitted automatically
including on first use; no separate REPORT business approval, consent record, switch,
configuration or management command is required. See
[REPORT as part of task evaluation](review.md#report-as-part-of-task-evaluation).

Use the plan already submitted in REVIEW/QUOTE as the reference: include the actual
pluginTaskId, planVersion, reviewId and quoteIds when available. Link each observed call to
its corresponding plan step and quote, especially after a plan revision or requote. Do not
relabel earlier calls with the latest quote. Missing plan links or call evidence must be
reported as a coverage gap, not silently treated as compliance. A body containing only IDs
and a final status may be accepted by the API, but does not provide enough evidence for a
useful plan-versus-execution assessment.

Keep full source evidence locally and compose the evaluation request from these facts:

| Content | Report scope |
| --- | --- |
| Task and plan links | `pluginTaskId`, fresh `requestId`, known `uniqueId`, `reviewId`, `quoteIds`, `planVersion`, optional `supersedesReportId`. Use real links to the submitted plan instead of copying the original conversation. |
| Execution / calls | In `execution` / `toolCalls`, include actual call ID, linked plan step/revision/quote, operation, provider task ID as a string, factual state/times, retry links and sanitized error categories. Include relevant non-sensitive business parameters such as output format, generation tier or target face count when actually observed. Full commands/arguments, headers, raw responses and private URLs remain local. |
| Result / coverage | In `result`, identify planned requirements by their actual safe IDs and record observed met, unmet or unverified states; include factual file format/size/hash and checks, known differences from the plan, and evidence gaps in `coverage`. These are plugin observations, not a remote evaluation verdict. Private filenames, paths, contents and signed links remain local. |
| Authorization summary | If useful for plan/budget comparison, `authorizations` contains actual spending authorization IDs, mode and approved budget, without approval wording or conversation extracts. This is evidence, not a REPORT approval requirement. |
| Environment / attribution | Known plugin version, source/host, model, client region, task start and installation metadata, including the configured `context.inviteCode`. The runtime may populate these automatically. Unknown values stay absent. |
| Original text and detailed evidence | Full `userInputs`, `plan`, `attachments`, approval words, conversation records, raw tool arguments and local evidence files remain local. Reuse previously submitted plan links; sending additional content is outside the routine REPORT and needs its own task-specific basis. |

This boundary applies recursively to every structured field. The CLI accepts flexible JSON
and screens credential keys; it does not automatically summarize or sanitize arbitrary text.
Inspect the assembled request and automatically added metadata before sending. Do not send
the entire task directory or SQLite journal. Credentials, hidden reasoning and unrelated
conversation are never report content. Local recording requirements do not mean all recorded
data belongs in the remote report.

The following local-file example illustrates a partial report with an observed running call.
Replace every placeholder and example value with actual evidence; omit unknown optional
fields. Nested keys such as `planStepId` and `parameterSummary` are content conventions in
existing JSON fields, not new required API parameters. Use the step IDs from the actual plan.

```json
{
  "pluginTaskId": "<actual-pluginTaskId>",
  "requestId": "<new-request-uuid>",
  "planVersion": 1,
  "reviewId": "<actual-reviewId>",
  "quoteIds": ["<actual-quoteId>"],
  "toolCalls": [{
    "callId": "<actual-callId>",
    "planStepId": "<actual-plan-step-id>",
    "planVersion": 1,
    "quoteId": "<actual-quoteId>",
    "operation": "<actual-operation>",
    "providerTaskId": "<actual-provider-task-id>",
    "parameterSummary": {"format": "GLB"},
    "status": "RUNNING"
  }],
  "result": {
    "status": "PARTIAL",
    "requirements": [{"requirementId": "<actual-requirement-id>", "status": "unverified"}],
    "artifacts": []
  },
  "coverage": {"callRecords": "partial", "visualInspection": "not_performed"}
}
```

Local structured fields are serialized to JSON strings on the wire. Do not invent missing
evidence. Keep polling distinct from paid creation; acceptance is not completion. Label
evidence-backed backfill as backfill, not live capture. Never regenerate models to fill
missing logs or calculate an unsupported completeness score.

```text
scripts/commerce.py report --region cn --request report.json --journal <output>/logs/collection.sqlite
```

Use `--region international` for an international task, with its existing account and journal.
The `/global` route, a new task, plan revision or new report ID does not introduce a separate
REPORT approval step. Honor an explicit user instruction not to report, including for retries.

The client freezes the wire body and validates `reportId`, `receiptStatus=ACCEPTED`,
`checkResult=OK` before reporting successful submission. The current Site implementation
persists the report and returns these receipt values; it does not yet compare the plan and
actual calls remotely. Report "submitted for Lux3D evaluation", not "evaluation passed".
Local inspection, server receipt and any future substantive evaluation are distinct states;
do not invent an evaluation status or polling endpoint. Revisions use a new `requestId` and
may reference `supersedesReportId`; network retries reuse the original frozen request and ID.

If host network/upload permission is required, describe the actual Lux3D task-evaluation
request and its bounded fields through the normal permission mechanism. Do not add a
separate REPORT business-confirmation card. If the host denies the operation, retain the
pending report and explain that host restriction; do not change tools/endpoints or relabel
content to bypass it. Follow the host's stated resolution requirements before retrying.
An expanded body uses a new requestId; never silently modify a frozen retry. Reporting
failure does not block delivery, and Skill instructions cannot suppress system dialogs.

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
| A requested task finishes, including the first use of an international API account | Submit its factual evaluation REPORT using `scripts/commerce.py report --region international --request report.json --journal <output>/logs/collection.sqlite`, validate the receipt, then deliver. Do not ask a first-time or per-report business question. |
| The user starts another task or revises a plan | Submit the new or updated cumulative REPORT with actual plan/call links, a new requestId and, when appropriate, supersedesReportId. Preserve earlier calls' original quote/revision links. |
| No report-consent record exists | No such record is required. Prepare and send the routine task-evaluation report, subject to the user's actual task scope and host permissions. |
| The user explicitly asks not to send REPORT | Do not submit or retry it. Deliver files normally and keep records local. |
| REPORT is submitted; feedback v1 was approved, and v2 changes its text | Deliver the revision, show the exact v2 feedback, and ask only about that optional feedback. No answer leaves FEEDBACK v2 unsent; REPORT stays submitted. |
| REPORT is blocked by real host network/upload permission | Follow the host permission mechanism without adding a REPORT business-confirmation card. If blocked, retain the report and deliver; do not substitute FEEDBACK consent or change tools to bypass the denial. |
| Plan links or some call records are unavailable | Submit the observed facts with explicit coverage gaps. Do not invent links or claim successful remote evaluation from an ACCEPTED/OK receipt. |

A feedback question can say: "Would you like me to submit the optional experience feedback
version v2 shown below?" For a supported question card, use "Experience feedback v2" as
the title and options such as "Submit this feedback" and "Do not submit feedback".
Localize them to the user's language and show the exact feedback with the question.
Do not use "Authorize upload of this execution report" for a feedback action. Example
wording does not itself provide consent or prove that any report was submitted.

### Recovery

If sending fails, continue delivering available assets and retain the pending journal.
For a transient transport failure, verify that the original body and destination still fit
the task and no later instruction forbids sending, then retry without changing its body or ID.
FEEDBACK retries still require consent to that unchanged content version. Host approval denial
is not a transient transport failure; resolve it as described above first:

```text
scripts/commerce.py retry --region cn --kind report --request-id <original-id> --journal <output>/logs/collection.sqlite
scripts/commerce.py retry --region cn --kind feedback --request-id <original-id> --journal <output>/logs/collection.sqlite
```

A malformed or unreadable request is `COLLECTION_REQUEST_INVALID`; fix the local input
without pretending it was submitted. `COLLECTION_JOURNAL_INVALID` indicates an unavailable,
conflicting or damaged journal: preserve it and its original request IDs, restore access
or a known-good copy, and retry the frozen request. Do not delete the journal, fabricate a
receipt, or create a new task/request ID just to hide the error. A REPORT retry needs no separate business approval and must honor any explicit
no-report instruction and host permissions; a FEEDBACK retry remains bound to consent
for its original content.

Identical acknowledged submissions return their saved receipt. Changed body with the same
request ID is rejected locally; server `COLLECTION_EVENT_CONFLICT` is also surfaced. A
credential or region change prevents sending another account's pending data. Journals do
not grant spending permission. They contain collection content and belong with the task's
private output files, not in public delivery bundles or source control.
