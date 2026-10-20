
# Aholo Lux3D MCP workflow

This reference belongs to the single **aholo-lux3d** Skill in the **Common suite** package.
Use [the main entry](../../SKILL.md) to choose OpenAPI or MCP. Follow only the
selected mode; resolve it through the main entry and connection onboarding before calls.
Never silently switch modes or replay an uncertain create through OpenAPI.


After MCP mode is resolved by explicit choice or the onboarding rules, execute the requested
operation through **Aholo Lux3D MCP**. Aholo Lux3D supports **2D image operations as well as
3D assets**. Do not silently replace it with a host's image editor, Seedream,
another image model or another provider because a tool or file is missing.
Report the specific missing capability and help connect Aholo Lux3D. Use an alternative
only if the user chooses it, and name the provider actually used.

## First use: find the tools, then verify the connection

This Skill is shared by native ecosystem MCP plugins and the public-portal
Connector. A native installer may register the connection; importing a Skill
ZIP alone **does not automatically register or authenticate a remote MCP server
in every host**. Check and reuse a working connection before changing settings.
A Skill label in the conversation is not proof that its tools are connected.

1. Inspect this session's tool list. If the host supports deferred tool discovery
   (for example a tool-search facility), search for `Aholo Lux3D MCP`, `Aholo Lux3D`, `lux3d-mcp`, the
   required tool names below, and their task descriptions. Use the callable
   identifiers the host returns; it may add a namespace or display label.
   Check that their server provenance is the intended Aholo Lux3D connection.
2. For new generation, confirm account, quote, the selected create tool and
   `gettask` are callable and inspect their input schemas. For recovery, discover
   only the relevant query tools. A missing unrelated operation does not disable
   a supported one. **Perform discovery even if a local JSON file is missing.**
   Missing documentation does not prove that the remote server is disconnected.
3. If tools are absent, distinguish missing configuration, missing credential,
   pending host reload, authentication failure and missing operation using
   [connection onboarding](../connection-onboarding.md). Prepare supported non-secret
   setup within the user's request before asking them to act. Preserve a pending
   task's recorded IDs; absent tools do not mean an earlier task never started.
   Never diagnose a bad key from a timeout or dump a full setup tutorial by default.
4. After connection/reconnection, discover again. For new work, resolve host
   identity as below and call `getlux3daccountbalance` with the actual schema.
   Only a successful response verifies this session's authentication/account
   access; do not treat a timeout as a bad key. This account check does not create
   a generation task. Then proceed to inputs, plan, quote and authorized creation.

The connection settings are in this entry so tool discovery and setup do not
depend on finding a parent directory:

## Select one regional connection

Each ecosystem distributes **one Connector package for both regions**, with the same
workflow and tools. Choose the region explicitly, or reuse the user's established
choice; never infer it from language, location or a failed request. Bind this
task's calls to the selected regional connection and use only its API Key.
Do not disable another region globally just to select this task's route; its
credentials and pending tasks may still be in use. If the host cannot distinguish
server provenance, stop affected calls and resolve that ambiguity through supported
connection controls. Never require the other region's key. Follow
[connection onboarding](../connection-onboarding.md) before asking for manual setup.

| Region | Connection / server key | MCP URL | API Key |
| --- | --- | --- | --- |
| China (`cn`) | `lux3d-mcp` | `https://api.aholo3d.cn/lux3d-mcp/mcp` | [China key](https://labs.aholo3d.cn/api-keys?from=lux3d), `LUX3D_CN_API_KEY` |
| International (`international`) | `lux3d-mcp-international` | `https://api.aholo.ai/lux3d-mcp/mcp` | [International key](https://labs.aholo.ai/api-keys?from=lux3d), `LUX3D_GLOBAL_API_KEY` |

Both connections send the **raw regional API Key** in `Authorization`, without
`Bearer`. The international MCP URL does **not** have the OpenAPI `/global` prefix.
Do not pass a `region` argument to a tool unless its discovered schema accepts it;
region routing comes from the selected server, not source or agentName.

Discover tools on the selected server and verify their provenance, actual schemas
and successful account access before use. Same-named tools on the other connection
are not substitutes. Keep account, quote, create, query, REPORT and FEEDBACK on
the same selected connection. Persist connection, account, region, upload receipts,
quote context and task IDs together. Pending tasks and reports resume on their
original connection; switching regions starts a separate context and does not
move tasks, balances, quotes, credentials or authorizations across regions.
Never fall back across regions after an error. If the requested server or tool
is absent, preserve the task and explain the missing connection.

For “切换到海外” or “切回国内”, select the corresponding connection for new work,
verify its account access and obtain a fresh matching quote. Keep the other
region's saved credentials and task records. Report switching complete only
after verification; use the host's supported connection controls or guide the
user when this session cannot change them. Existing tasks keep their original region.

Store the key in the host's private connection settings. Never request it in
chat or write it into this package. This URL is an MCP transport endpoint, not
an image URL or a JSON REST endpoint for directly posting arbitrary tool names.
Typing a tool name in a reply is not invoking it.

Explain the observed state and the single remaining user action in plain language.
For example, only after non-secret setup is actually prepared: “海外连接配置已准备好，
还需要你在私密设置中填入海外 API Key。完成后我会检查账户并继续场景报价。”
If setup cannot be applied, say precisely why and provide the smallest supported
manual step. Do not claim configuration, authentication or generation has succeeded
without evidence. Preserve the creative brief while setup is pending.

## Route the request to the correct Aholo Lux3D tool

These are expected server tool names, not a substitute for the live schemas.
Match the discovered callable and read its required arguments, reference-input
fields and body/envelope before calling; never guess a `prompt`, image field or
outer `body` shape when the schema is available.

| Task / operation | Expected tool | How to use it |
| --- | --- | --- |
| `account` | `getlux3daccountbalance` | Read current account facts and the quote `uniqueId`. |
| `quote` | `post_quotelux3dopenapirequests` | Price the numbered plan of canonical OpenAPI create requests. |
| `multimodal-image` | `post_createmultimodaltoimagetask` | **2D** image generation or reference-based image changes using the discovered text/image inputs; inspect this for hair, clothing or background edits. |
| `four-view` | `post_createimagetofourviewtask` | Create four views when the requested plan needs them. |
| `image-to-3d` | `post_createimgto3dtask` | Create a 3D asset from prepared image inputs. |
| `text-to-3d` | `post_createtextto3dtask` | Create a 3D asset from a text description. |
| `material-transfer` | `post_creatematerialtransfertask` | Apply a requested material change to a model. |
| `multi-format-export` | `post_createmultiformatexporttask` | Convert/export a model to supported target formats. |
| `mesh-retopology` | `post_createmeshretopologytask` | Retopologize a static non-Draco GLB to GLB/OBJ, with optional baked texture ZIP. |
| `articulation-animation` | `post_createarticulationanimationtask` | Add joints and motion to model parts using only `glbUrl` and `prompt`. |
| `auto-rig` | `post_createhumanoidautorigtask` | Produce a rigged character GLB from `modelUrl`. |
| `animation-retarget` | `post_createhumanoidanimationretargettask` | Apply 1–10 selected public actions to a rigged GLB; separate/combined GLB or FBX. |
| `get-task` | `gettask` | Query a returned Aholo Lux3D task ID and retrieve real result URLs. |
| `list-tasks` | `get_listtasks` | List this account's tasks for discovery or recovery. |
| `report` | `post_reportlux3dtask` | Close out the creative task with an execution report, including partial or failed work. |
| `feedback` | `post_submitlux3dexperiencefeedback` | Submit optional experience feedback only with consent to its exact version. |

Read [model processing and animation](references/generation.md) and the
[published generation schemas](generation-tools.json) before using these four
operations. Their mappings are verified from the published configuration;
current-session discovery and successful account access remain required.
Do not infer that an unavailable tool is callable from the reference snapshot.

Read the [public animation IDs](animation-ids.json) when selecting retargeting
motions. Preserve case; select 1–10 distinct IDs from this shared catalog.

For “把头发换成红色长卷发，重建图片里的场景”, inspect the multimodal **image**
tool when the intended result is an edited picture; do not conclude that Aholo Lux3D
only supports GLB/OBJ/FBX. If “重建场景” could mean an editable 3D asset, clarify
that deliverable before quoting a different workflow. Preserve the subject and
requested changes. A 2D image is not evidence that a 3D scene was reconstructed.
If the discovered tool does not support the needed image inputs, report that
specific limitation without silently choosing another provider.

For an explicit “先用 Aholo Lux3D 改图，再做场景/3D 重建”, plan both requested stages:
`post_createmultimodaltoimagetask → gettask → edited image → unified Asset/OUS
upload → post_createimgto3dtask → gettask`. Use actual supported schema fields
and quote/authorize each intended stage, using staged quotes when the next input
depends on the first result. Do not invent the edited URL before task completion.
Retain the edit result if the 3D stage is blocked, and report partial completion;
do not present the edited picture alone as the requested 3D result.

## Execute the chosen operation

1. Identify the requested deliverable and selected Aholo Lux3D operation. Prepare all
   file inputs through the unified upload below; preserve their order and role.
2. Use the verified account context and [tool map](tool-map.json) to build a
   numbered plan. Quote the **canonical `/lux3d/v1/...` paths**, not MCP tool names.
   Follow [Planning and quotes](references/planning.md) for parameter encoding.
   Initialize one persistent `pluginTaskId` and include the complete versioned
   plan in REVIEW/QUOTE as described in [Collection](references/collection.md).
3. Show the actual returned quote and apply [Review and approval](references/review.md).
   Reuse existing authorization within its scope; choosing a Connector alone
   does not introduce another confirmation requirement. Unknown prices are not free.
4. Invoke the selected discovered create tool once. Record the real returned
   task ID as a string immediately; creation accepted is not task completion.
5. Query `gettask` until completion or the bounded wait expires, following
   [Execution and recovery](references/execution.md). Return actual result URLs
   and truthful status. Do not retry an uncertain create or switch providers to
   conceal its failure. Do not claim a Aholo Lux3D result without a Aholo Lux3D task/result.
6. Submit the permitted execution REPORT automatically at closeout. Deliver
   available results even if reporting is pending. Optional FEEDBACK requires
   explicit consent to its exact text/version after delivery; follow [Collection](references/collection.md).

## Task concurrency

Free users may have at most **5** shared generation tasks in progress; paid
users **20**. Resolve membership from the current account response. Part
splitting has a separate limit of **5** for all users and is not currently
integrated by this plugin. Count existing account tasks and reserve slots
before parallel dispatch; see [Execution limits](references/execution.md#account-task-concurrency).

## Upload every file input through Asset/OUS

Upload is supported through the public Asset API, **not** provided by the mapped MCP
tools: `GET /asset/v1/token → OUS upload → successful status URL`. It uses the
**same selected-region API Key as MCP**, securely injected into the Asset request;
MCP login alone does not expose the stored secret to an HTTP tool.

Local files are uploaded; external and host-attachment URLs must first be
downloaded and then uploaded through this same chain. Only a completed unified
upload URL or a matching valid upload receipt may enter Aholo Lux3D input fields.
An unrelated “upload file” tool returning a public URL is not sufficient.
Compute whole-file MD5 first, use the token's `blockSize` for single/part upload,
and wait for `status=5` and a real returned URL. Read
[Unified input upload](references/upload.md) for exact fields and credentials.
If the host lacks this upload capability, report it before the affected create;
never pass the original URL through as a workaround. Final output links sent to
the user do not require re-upload unless they become another operation's input.

## Host identity and bundled resources

Resolve the actual current host from [the registry](host-identity.json) or the [optional helper](scripts/host_identity.py). Keep the same automatic identity on account and quote calls; verify live schemas or supported host injection. Never infer it from the model provider.

Keep the complete suite installed. Resolve connection.json, tool-map.json, body.md,
references/ and scripts/ relative to this workflow file. This reference directory
is not another Skill or a standalone installation.

Use only the selected regional MCP connection for this task. Follow [connection onboarding](../connection-onboarding.md) to reuse or prepare the host connection and request only a missing private credential or required reload. The connection.json descriptor is host-neutral; importing this suite does not register MCP. Do not require Python for MCP-only work; uploads still require the Asset/OUS flow and secure access to the selected regional key.

Read [connection setup](README.md) and [the MCP workflow](body.md). Actual tools and
authentication require live verification. Communicate in the user's language.
