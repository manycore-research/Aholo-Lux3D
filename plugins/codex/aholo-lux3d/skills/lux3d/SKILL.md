---
name: lux3d
description: "Use Lux3D to generate or process 3D assets, resume existing tasks, and deliver verified source files with an offline preview. Use when the user requests Lux3D creation, asset delivery or project integration; assemble scenes with local Blender or an available Blender MCP."
---

# Aholo Lux3D

Read [the production workflow](body.md), then load the reference for the current
stage. Use the bundled runtime from this installed Skill, resolving commands
against its actual directory rather than another Lux3D checkout or cached Skill.

Keep shipped instructions in English; communicate, clarify and summarize in the
user's language. Codex owns intent, project inspection and user authorization.
Codex also records submissions and resumes their task IDs. The runtime provides
API validation, generation calls, task queries and deterministic delivery.

## Prepare Python before using tools

This is the `aholo-lux3d:lux3d` Skill. The older `lux3d-workflow` plugin is a
separate installation; use this Skill's files when the user selects this plugin.

Before the first Python tool call, run:

```text
python3 <installed-skill>/scripts/setup_runtime.py
```

On Windows, use an available Python 3 launcher instead of `python3`. The setup
command creates or reuses a private environment, installs the bundled runtime's
declared dependencies, and returns its absolute `python` path as JSON. Use that
interpreter for bundled Lux3D scripts and Python API calls. Local Blender scripts
run inside Blender with its own embedded Python, as described in the assembly reference.
Reuse it while it remains available. Setup does not call Lux3D or require an API key.

For `CLI_DEPENDENCY_MISSING`, rerun setup and retry the original action with the
returned interpreter. If installation fails, report the dependency setup issue
and preserve the request. A Python import failure does not mean the API key is
invalid or that generation tools are absent. Bundled command-line tools are
usable tools even when there is no corresponding MCP tool. Check their actual
entrypoints and errors before declaring a capability unavailable.

## Account and quote tools

Run the bundled `scripts/commerce.py` with an explicit region. Configure
`LUX3D_CN_API_KEY` for `cn` or `LUX3D_GLOBAL_API_KEY` for `international` in secure
environment configuration; never put keys in command arguments or quote files.
The Codex release unit's `adapter.json` fixes `source=1` and the CLI rejects
source overrides. Requests use public OpenAPI with raw API-key Authorization.
The runtime selects the regional domain and adds `/global` only to international
HTTP request paths. Quote-item `endpoint.path` stays `/lux3d/v1/...` in both
regions; see `core/contracts/lux3d-generation.v1.json` for endpoint definitions.

```text
python <installed-skill>/scripts/commerce.py balance --region cn
python <installed-skill>/scripts/commerce.py quote --region cn --items <items.json>
```

The quote file is the sequence-keyed `items` map described in
[planning](references/planning.md), without a `source/uniqueId/items` envelope.
Parameter groups may be objects or serialized JSON Strings. The command checks
input, refreshes the balance, then quotes with the server-issued `uniqueId`.
It returns `{account, quote}`; balance alone returns the account snapshot.
Errors are safe JSON on stderr with nonzero exit status, never zero-cost facts.
This tool does not submit generation tasks or approve spending. Before submitting,
Codex checks that the successful quote is still valid and matches the actual work,
then applies the approval rules. Follow [execution](references/execution.md) to
call the existing client submission functions and save each task ID. This path
does not require the unfinished workflow runner adapters; it also does not claim
runtime-enforced approval, budget limits or duplicate-submission protection.

## Delivery

For local outputs, follow [results and delivery](references/results.md).
Deliver all items and an optional assembled scene in one self-contained
`preview.html`, with originals and `lux3d-delivery.json`. For a scene request,
read [model assembly](references/assembly.md) and
[external Blender collaboration](references/blender-collaboration.md). Codex can
run local Blender with a Python script or use an available Blender MCP. This
plugin supplies neither Blender nor an MCP server; MCP is not a prerequisite.

Provide links or paths to the model files and final HTML; do not open the preview
automatically. When the user asks to view it, use an available file/browser viewer.
Report only checks actually performed. A successful download, fixture test,
supplied tool record or generated HTML is not by itself full acceptance.
Keep already completed assets available if an external capability is missing.
