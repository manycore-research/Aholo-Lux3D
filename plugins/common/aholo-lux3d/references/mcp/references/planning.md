# Planning and quotes through MCP

Preserve the user's requested assets, quantities, references, independence and
deliverables. Reuse suitable existing tasks and assets. Check the current tools'
input schemas and actual output support before promising a format or local
delivery. Before quoting or creating, prepare every file input with the
[unified Asset/OUS upload](upload.md). Local files are uploaded directly;
external URLs must first be downloaded by the host and then uploaded through
that same chain. Never pass an arbitrary URL through just because the host can
read it. Only a successful unified-upload URL, or its valid existing receipt,
is eligible for the corresponding MCP input. Resolve missing upload capability
before the affected call. Text-to-3D does not need an image unless the chosen
request requires one. Include dependencies, optional enhancement and conversion
in the plan and quoted cost.

The [tool map](../tool-map.json) maps business operations to tool names and
canonical OpenAPI paths. Use `getlux3daccountbalance` with the installed identity
to obtain a current account context and `uniqueId`, then use
`post_quotelux3dopenapirequests` to quote the numbered plan. Source 100 requires
the same automatically resolved real host `agentName` on both calls. Known hosts
retain their registered source and send their canonical name in quotes. Resolve
both values from the shared registry each session, without changing the package.

Each `items` key is a positive integer string. Each create item's endpoint method
is `POST` and its path is the original `/lux3d/v1/...` path from the mapping.
Never use a tool name, domain, query string or `/global` prefix as a quote path.
Account, task lookup, task-list, REPORT and FEEDBACK operations are not billable quote items.
Include the persistent creative `pluginTaskId`, positive integer `planVersion`
and complete plain-text `plan` in the quote body for combined REVIEW/QUOTE.
Follow [Collection](collection.md) for structured input encoding and receipts.
Use [generation instructions](generation.md) for retopology, articulation,
auto-rig and retargeting. Their quote paths are canonical OpenAPI paths; the
server owns the separate internal SOA routing. Never use `/api/open/...` in a quote.

Prepare parameter groups as objects internally. At the quote HTTP boundary,
`pathParameters`, `queryParameters` and `body` are JSON strings containing
objects. For the ten create paths, the first two are the literal string `"{}"`.
Serialize the intended generation body exactly once; follow the live MCP schema
for its outer argument envelope. The create call itself uses the actual request
shape, not quote metadata or encoded quote strings. `uniqueId` is account context,
not a task ID or idempotency key; do not add it to create calls.

A quote supports 1–50 calls. Preserve the sequence-to-asset mapping when displaying
item costs, split larger plans into quote groups, and include the full intended
cost. Future inputs that affect price require staged quotes. Do not invent fixed
prices or interpret an error, unknown price or trial entitlement as zero cost.
A quote is an estimate, not a reservation or proof of settled charges.

Show the returned total, relevant item costs and validity before applying the
shared [Review and approval](review.md) rules. Refresh a quote when its plan,
account, region, identity, context or validity changes. Account refresh can
invalidate an earlier `uniqueId` and its quotes. A refreshed quote alone does not
invalidate existing authorization when its scope and cost still fit.

For Chinese plan tables display G1 as `标准版` and G1-Turbo as `极速版`; in English
use `standard` and `turbo`. Preserve API version values in requests. Determine
supported output formats from the live operation schema and returned metadata;
there is no bundled output-format helper. Display `obj_zip` as OBJ and `fbx_zip`
as FBX while explaining archive packaging separately. If an output cannot be
confirmed, label it unknown rather than promising it.

Keep quoteId in host state. At creation, use it as `body.contentId` for
all nine supported create tools other than articulation, when accepted by the live schema.
Articulation accepts only `glbUrl` and `prompt`; add no trace or identity fields.

A missing, rejected or expired quote blocks the corresponding create, even if
the MCP creation tool is published and callable. Do not fall back to fixed
prices, a different path, or unquoted creation after a pricing error.
