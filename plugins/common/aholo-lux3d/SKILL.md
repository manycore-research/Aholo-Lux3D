---
name: aholo-lux3d
description: Generate and process Lux3D assets, rig characters, retarget animations and resume tasks. One entry supports OpenAPI and MCP; choose the execution mode and region, then follow that workflow.
---

# Aholo Lux3D

This suite has one Skill entry and two execution modes. Communicate in the
user's language. Reuse the user's established mode and region; if either is
unknown, ask before account, quote or create calls. Do not choose based only
on available tools, language, location or a failed request.

| Selected mode | Workflow | Required host capabilities |
| --- | --- | --- |
| OpenAPI | [OpenAPI workflow](references/openapi-workflow.md), then [production workflow](body.md) and its stage references | Local Python 3.10+, file access, HTTPS and secure credential injection; the complete runtime, contracts and offline viewer are bundled |
| MCP | [MCP workflow](references/mcp/workflow.md) and [connection setup](references/mcp/README.md) | A remote MCP client, live tool discovery and secure credential configuration; input uploads additionally require the documented Asset/OUS flow |

Read only the selected workflow as the execution instructions. Resolve paths
from this installed `aholo-lux3d/` directory, independent of the current working
directory. MCP reference paths are relative to `references/mcp/`; OpenAPI scripts
and core resources are at the Skill root. MCP-only tasks do not require Python
setup merely because this suite also contains the OpenAPI runtime.

Both modes support China (`cn`) and international (`international`). Choose the
region explicitly and use only its connection and credential. For MCP, enable
only that region's server in the host. The bundled connection descriptor is
host-neutral; loading this Skill does not register or authenticate MCP.

Resolve the actual host automatically using the bundled identity registry and
the chosen workflow. Use the real host application, never the model provider.
Record mode, region, connection/account, plan version, quotes, upload receipts,
authorizations and actual task IDs together. Switching mode, region or account
starts a new context and requires fresh account and pricing checks. Resume
existing tasks and reports on their original route. Reconcile uncertain create
results before any further create; never automatically replay a create through
the other mode or region.

Both workflows preserve the same planning, pricing, approval, REPORT and delivery
rules. REPORT includes the complete versioned plan and task-related original
inputs, actual execution and results for remote expert evaluation within the
authorized scope. A valid successful REPORT receipt means remote evaluation
passed; it is separate from user acceptance and permission for additional cost.
Follow the selected workflow's receipt checks and FEEDBACK consent rules.

The maintained GitHub source is the installation input. Follow the repository's
AGENTS.md and local installer; archived packages are provenance references. Keep
an optional installation invite code in `.aholo-lux3d-installation.json` beside
the installed Skill, never inside it. OpenAPI loads it through the bundled
runtime; MCP forwards it through supported collection `context` fields as
described in [installation attribution](references/mcp/references/collection.md#installation-invite-code).
Do not ask for an absent code or change attribution on resumed tasks or retries.

Install the complete suite into one `aholo-lux3d` Skill directory. Use the host's
supported replacement controls for an existing installation, preserving user
assets, task history, credentials and working MCP connections. Keep one Skill
entry for both execution modes.
