# Supplied scene delivery contract

This is the local ingestion contract for an **already exported** scene. It is
not a Blender MCP tool schema, scene solver, or proof of end-to-end acceptance.
The plugin runtime never translates assembly intent into transforms or runs
Blender. Codex may invoke local Blender through a host command or use Blender MCP.

## Input

In a `lux3d.delivery-spec/v2` document, after selecting each item's delivered
attempt, provide:

```json
{
  "scene": {
    "status": "ready",
    "artifactPath": "assembly/scene.glb",
    "evidencePath": "assembly/execution.json"
  }
}
```

Both paths resolve relative to the delivery-spec file, not the working directory.
The GLB must have a scene, nodes and mesh, pass the existing container checks,
and have embedded buffers/images (BIN, buffer views or data URIs). Browser parsing
and visual inspection remain separate checks; these checks are not a complete
glTF semantic validator and do not establish correct assembly relationships.

The JSON execution record must have exactly these fields (placeholder values
below must be replaced with actual values):

```json
{
  "schema": "lux3d.scene-execution/v1",
  "kind": "external-tool",
  "toolName": "actual-discovered-tool-name",
  "callId": "actual-tool-call-id",
    "recordRef": "session:actual-session-id/actual-tool-call-id",
  "executedAt": "2026-09-08T10:00:00Z",
  "exportSha256": "replace-with-exact-export-file-digest",
  "sources": [
    {
      "itemId": "chair",
      "attemptId": "chair-generation",
      "artifactId": "chair-generation:glb",
      "sha256": "replace-with-source-artifact-digest"
    }
  ]
}
```

- `kind` is `external-tool` for an actual supplied execution record, including
  a host command running local Blender, or
  `development-fixture` for synthetic tests. Never relabel a fixture as external.
- The tool name, call ID and record reference are opaque identifiers, using
  ASCII letters/digits and `:._/-`, starting with a letter/digit, up to 512
  characters. URLs, absolute paths, whitespace and signed links are rejected.
  The reference identifies an independently inspectable tool/session record;
  its existence is not automatically verified by this offline command.
- `executedAt` is the recorded tool execution time with explicit timezone,
  not a Lux3D task creation time. Do not fill it with packaging time.
- Each source must match a selected item attempt and its actual delivered
  artifact bytes. Reusing one artifact for several items is explicit through
  separate bindings; duplicate item/artifact bindings are rejected. An assembly
  may reference a requested subset of the independent items.
- Export and source digests bind the record to bytes. They do not prove the
  correctness of transforms, geometry, or execution claims.
- No duplicate JSON keys, extra fields, credentials, temporary URLs or raw
  credential-bearing tool outputs are accepted in this delivery record. Keep
  the actual tool schema/transcript in its original controlled record system;
  do not put it in these fields or fabricate a transcript.

## Output and failure semantics

Successful ingestion adds `scene/scene.glb` and `evidence/scene-execution.json`,
both copied byte-for-byte and embedded in the HTML. Their manifest artifact roles
are `assembled-scene` and `scene-execution-evidence`. The latter has format
`json`; it is not a generation output format or a cloud task.

`manifest.scene` references these artifacts, source bindings and normalized
execution metadata. It always records
`verification: supplied-record-not-independently-verified`. `ready` means the
supplied export passed ingestion checks, not that Blender E2E is certified.
The page shows this distinction, labels development fixtures, shows source
items/tasks, and provides original GLB and evidence downloads. No additional
cloud task or credit charge is inferred from this local scene.

An unreadable/corrupt export, invalid evidence, mismatched bytes or stale selected
attempt produces `scene.status=failed` with `scene-validation-failed`, preserving
the independent item bundle and incomplete overall status. Invalid scene files
or evidence are not distributed. Malformed scene request shape is rejected at
the input boundary. I/O failures during final copying still stop publication
of the completion manifest; previous delivery directories are never overwritten.

Without an exported scene, use `not-requested`, or use `unavailable`, `pending`
or `failed` with a reason. If neither local Blender nor Blender MCP can be used,
assembly is `unavailable`; the independent assets remain deliverable. Missing
MCP alone does not prevent local assembly. None of these outcomes starts a new generation.

## Acceptance evidence still required

Actual command/API or MCP schema, invocation, approved assembly relationships,
export and visual inspection must be checked independently before claiming a
real assembled-scene acceptance. Local fixtures and supplied records do not
replace that gate. The current automated suite establishes ingestion, isolation,
same-page viewing and byte preservation only.
