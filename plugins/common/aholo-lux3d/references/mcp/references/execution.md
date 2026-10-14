# Execution and recovery through MCP

Before submitting, establish the actual connection and identity as described in
[MCP workflow](../body.md), confirm each file input has a successful
[unified-upload receipt](upload.md) and uses its returned URL, obtain a current matching
quote and apply [Review and approval](review.md). The base package's unverified
qualification flags do not grant permission to bypass host/endpoint acceptance.

## Keep the original regional connection

Bind each task and pending report to its original server, account and region.
Use only tools discovered on that server for account, quote, creation, polling
and collection. Selecting another region does not change an existing task's
origin. Never replay an uncertain create, move a pending report or reuse an
account context on the other server. See [Regional selection](../body.md).

## Account task concurrency

The account's shared generation task limit is **5 for free users** and **20 for
paid users**. Use the current successful account response: boolean `member=true`
selects the paid/pro limit; `member=false` selects the free limit. Do not infer
paid status from a positive credit balance, a top-up, trial access or the host.
If membership is unknown, refresh the account before using the paid limit and
use at most the free limit while the other account/quote requirements remain met.

These limits count unfinished asynchronous tasks, not simultaneous HTTP requests
or calls per second. States 0, 1 and 2 occupy slots. Count the account's existing
active tasks across operations, API keys, hosts and Skill/MCP sessions; changing
source, quoteId or connection does not create a fresh quota. All nine generation
operations, including retopology, articulation, auto-rig and animation retargeting,
share this pool. One retarget create with several action IDs occupies one slot.
Multi-format export remains outside this shared generation pool; do not invent
an export quota from the generation limit.

Use one account coordinator to reserve available slots before dispatching ready,
authorized and quoted steps. Available slots are the limit minus observed active
tasks and local reservations not already represented by those tasks. Dependencies
must be ready before submission. Release a reservation on an explicit rejection
that created no task, or after observing a terminal provider state. Creation HTTP
completion, query timeout, local download failure and an uncertain submission do
not release a task slot. Reconcile uncertainty before creating again. If task-list
coverage or durable coordination is unavailable, serialize work conservatively
instead of assuming all slots are free. Limits are ceilings, not a target count.

**Part splitting has a separate per-account limit of 5 for every user**, including
paid users. Do not apply the paid generation limit of 20 to part splitting. This
policy does not add a part-split tool: the current plugin has no part-split route;
only invoke such an operation after its actual interface has been integrated and
discovered. The server may also enforce global capacity or account-specific limits.

On `GENERATION_CONCURRENCY_LIMIT_EXCEEDED`, pause new creates, keep/query existing
task IDs and wait for capacity. Never retry an uncertain create, switch accounts
or endpoints to evade the cap, or regenerate to recover a delivery failure. A
successful account/quote does not reserve server slots or authorize new spending.
The host coordinates this workflow through instructions; the server remains the
authority across processes and devices. No new server-side semaphore is installed.

Use a stable operation ID and retain the exact plan digest, account isolation
reference, region, source, normalized Agent name, connector mode, quote validity
and task ID when known. Keep task IDs as decimal strings to avoid numeric
precision loss. Where available, persist these records in private host state,
separate from portable deliverables. A stored `approved=true` or copied budget
ledger is not conversation authorization. When automatic execution is authorized,
one coordinator must reserve its quoted budget before parallel dispatch. If
durable tracking is unavailable, disclose the limitation and serialize work;
stop new spending if authorization or prior attempts cannot be reconciled.

Track planned, quoted, authorized, submitting, submitted and completed/failed
stages. Mark a timeout or ambiguous response during creation as
`submission-unknown`, preserve its commitment and reconcile before any further
attempt. Submit each exact quoted create request once. Without verified server
idempotency, never automatically retry a create call over the network, another
endpoint or the other mode. `uniqueId` does not provide idempotency. Client or
instruction locks cannot guarantee exactly-once execution across devices.

Use `gettask` for a known task ID and `get_listtasks` to find reliable records for
the authenticated account. Matching a prompt or filename alone cannot identify
an uncertain submission. Preserve the original identity, account and mode when
recovering; if evidence is inconclusive, pause new creation and report that state.
Do not interpret a query timeout as a failed remote task. Report cancellation or
refund only when the service actually confirms it.

Follow the installed descriptor's request and polling limits: one create attempt,
at most three attempts for a read-only operation, bounded backoff and polling.
Quote uses POST and is not covered by automatic read-only retry. Honor host
response/download limits. A polling or size limit pauses local work and leaves
the task recoverable; it does not mean remote failure. Never change regions to
work around an error. Failed local delivery resumes delivery only.

For delivery, use genuine artifact URLs returned by task results, or download
through an available host tool and verify its actual local output. Temporary
URLs may expire. Do not represent remote filesystem paths as local files.
Check the live tool schema and returned asset metadata for available model
formats; unsupported output formats cannot be inferred from a ZIP. Preserve
source models and identify partial success honestly.
The shared review's mention of output-format helpers applies only when the host
actually provides such a helper. This Connector bundles none; use the live
schema and returned metadata above instead of looking for a missing script.

Offline preview, Blender assembly, scene rendering and local inspection depend
on available host capabilities. Do not promise these outputs unless the host can
produce and verify them. This package includes an optional identity helper, but
does not bundle local 3D execution or a viewer.
Diagnose failures with redacted error codes, mode, resolved host, region and operation
reference; keep credentials, signed URLs and other users' records out of logs.

For the four new model operations, follow [generation result handling](generation.md):
preserve optional empty retopology ZIP slots, actual articulation file formats,
rigging errors and per-action partial retarget results. The published create
request uses an object under `body`; query uses the actual `gettask` schema.

At closeout, follow [Collection](collection.md): retain the actual call evidence,
submit the permitted REPORT without a separate business-confirmation question,
and keep a frozen pending request if submission is unavailable. Delivery does
not wait for a receipt or optional FEEDBACK consent. FEEDBACK requires explicit
consent to its exact version after delivery.
