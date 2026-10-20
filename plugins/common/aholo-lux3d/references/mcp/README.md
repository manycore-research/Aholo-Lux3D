# Aholo Lux3D MCP

These shared MCP instructions, connection descriptor and tool map are used by
both the public-portal Connector and native ecosystem MCP plugins. Their wrappers
provide host-specific packaging, registration and installation metadata; the
business workflow and tool rules remain the same. The public portal supplies one
universal Connector ZIP; native ecosystem releases may publish their own packages
to their marketplaces. Users do not select a profile or edit source attribution.

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

## Use the bundled MCP mode

Use the single [aholo-lux3d entry](../../SKILL.md) and choose MCP. Keep the complete
suite installed; these documents are supporting references.

Use only the selected regional MCP connection for this task. Follow [connection onboarding](../connection-onboarding.md) to reuse or prepare the host connection and request only a missing private credential or required reload. The connection.json descriptor is host-neutral; importing this suite does not register MCP. Do not require Python for MCP-only work; uploads still require the Asset/OUS flow and secure access to the selected regional key.

Discover live tools and input schemas, then verify account access and host identity.
Loading instructions alone does not connect MCP. No paid create is needed as a
connection test. Follow [the MCP workflow](workflow.md).

## Prepare file inputs through the unified upload

Every input file URL passed to Aholo Lux3D must come from the unified Asset/OUS upload.
For a local attachment, upload its bytes. For an external URL (including another
host uploader's URL), download the file first, then use that same Asset/OUS
flow. Only use the `url` returned by successful upload status, or reuse a matching
completed upload receipt. An externally accessible URL may be unreadable by
Aholo Lux3D's internal services and must not be passed through directly.

Read [Unified input upload](references/upload.md) for the exact
token, whole-file MD5, dynamic block-size, multipart and status steps. The mapped
MCP tools do not expose upload. This Asset path uses the same selected-region
Aholo Lux3D API Key as the MCP connection; no separate upload key is required.
The host needs either this specific upload
integration or file/HTTPS tools with supported secure credential injection.
Connecting MCP alone does not make its secret available to those tools. If a
required capability is missing, configure it through the host before creating
the affected task; do not fall back to submitting the original URL. Account,
quote, generation and task operations continue through MCP after preparation.

## Automatic host identity

The host obtains its real name from the current session and resolves it through
[host-identity.json](host-identity.json). The optional Python helper is
[scripts/host_identity.py](scripts/host_identity.py). Hosts without Python apply
the same registry rules themselves; no separate download or implementation is
required. Users never select an ecosystem or manually assign `source`.

| Actual running host | source | agentName |
| --- | --- | --- |
| Codex | 1 | `codex` |
| Claude Code | 2 | `claude-code` |
| DeepSeek | 3 | `deepseek` |
| WorkBuddy | 4 | `workbuddy` |
| Another host, for example 豆包 | 100 | Actual trimmed host name, for example `豆包` |

Known host aliases compare without case sensitivity. Unknown names preserve
case after trimming; blank names, controls, surrogates and names over 128
characters are invalid. Account calls require the real name for source 100;
quotes require it for every source. Derive these request parameters from the
session for each installation; never hard-code one host into these shared files.

This shared layer defines portable contents and installation steps. Whether a
particular Codex, DeepSeek or 豆包 client/version supports local Skills, remote
MCP, custom authentication and identity forwarding must be checked against that
client and the ecosystem wrapper being installed. Shared contents alone do not
prove native installation or live connector acceptance. Preserve the qualification
state in the descriptor and verify the
affected integration before billable creation.
