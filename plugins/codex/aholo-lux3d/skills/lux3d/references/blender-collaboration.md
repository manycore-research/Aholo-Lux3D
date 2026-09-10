# External Blender collaboration

Read this for an explicit assembled-scene request. Multiple unrelated items are
independent by default. The same final HTML shows independent assets and, when
available, the assembled scene; separate HTML files are not the delivery model.

## Discover and clarify before promising a scene

Follow [model assembly](assembly.md) to choose local Blender or an available
Blender MCP. Codex/GPT owns intent recognition and invocation through either
route. Local shell execution of Blender Python is a usable tool route even when
no MCP tools are listed. Check the installed Python API or the actual MCP schemas
for import, scene inspection, transforms and GLB export. Do not assume a universal
MCP name or schema. Mark assembly unavailable only when neither route is usable;
preserve independent assets and explain the actual blocker.

Before assembly, inspect source model dimensions and coordinate systems.
Ask only for consequential missing relationships: which objects participate,
relative placement/orientation, attachment or hierarchy, and real scale/units.
Use the approved plan's placement constraints when writing the script or tool
calls. Preserve the confirmed relationships and any explicit numeric transforms
in the host task record. Do not ask users to author a guessed MCP payload.

## Invoke and verify through the host

Use Blender Python or the actual MCP tool schema to import the selected source assets, apply the
confirmed relationships, inspect the resulting scene and export an embedded
`scene.glb`. Preserve originals. Confirm objects, relative transforms, scale and
materials in the actual result. A successful tool response alone does not prove
the exported bytes exist or that assembly meets the user's requirements.

Lux3D supplies assets; the host and external tool perform assembly. The plugin
implements no transform solver, Blender scene builder, MCP schema mapper or
HTML editor. This boundary does not prevent Codex from using genuine available
tools for an authorized scene request. `.blend` is an optional explicitly
requested extra, not a required intermediate or default delivery.

## Ingest evidence and display

Read [the scene delivery contract](../core/contracts/scene-delivery.md). Bind the actual
export to each selected source item/attempt/artifact and its inspected digest.
Use real tool/call identifiers, the actual execution time and an independently
inspectable session reference. A local Blender command is also an external-tool
invocation: retain its script, command, output and exported files, and use actual
host command/session identifiers in the record. Do not invent an MCP identity
for a local command. Keep raw tool schemas/transcripts in the host's
controlled record, not in the portable evidence. Never fill absent execution
facts with guessed IDs or synthetic evidence.

If tool results expose no recoverable invocation reference, preserve the assets
and explain the missing acceptance evidence; do not invent it to force `ready`.
Successful ingestion means a supplied record and export passed local validation.
The manifest labels it `supplied-record-not-independently-verified`; genuine
assembly acceptance additionally needs actual call/export and visual evidence.

Put the scene and independent items into the same delivery spec and run the
ordinary offline prepare command. On missing tools, failed assembly, invalid
export or missing evidence, preserve the independent items and report
`unavailable`, `pending` or `failed` with a reason. Do not relabel a group of
unassembled models as a scene or rerun charged generation to repair it.
