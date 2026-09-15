# Scene assembly and rendering

For architectural shell modeling, scene composition, multipart assembly, layout changes, lighting, cameras, animation, or rendered images/video, use local Blender or an available Blender MCP. The host agent translates the user's spatial relationships, visual direction, and shot requirements into a Blender Python script or actual MCP calls. Lux3D supplies the generated assets; the plugin does not implement a scene builder or copy or pin an MCP schema.

## Check the environment and tools

Check for a usable Blender executable or an available Blender MCP. Distinguish an absent application, a stopped application, and a missing MCP connection.

- For local Blender, resolve its executable from the installed application or `PATH` and check `--version` and `--help`. On macOS, the usual application executable is `/Applications/Blender.app/Contents/MacOS/Blender`; verify that it exists. Use the installed version's Python API for import, object transforms, lighting, cameras, animation, rendering, scene inspection, and export.
- Run a task-local Python script with the actual executable, for example `"<blender-executable>" --background --factory-startup --python-exit-code 1 --python "<assembly.py>"`. This starts a separate background process, requires no open Blender window or MCP connection, and leaves the user's open document alone. Use Blender's embedded Python for `bpy`, not the Lux3D API environment. Open the GUI only when needed for the requested interaction or inspection; the user need not launch Blender manually.
- If using MCP, discover the available tools and read their actual schemas. Do not guess tool names or parameters. If MCP is missing or disconnected, use local Blender when available instead of stopping or requiring MCP setup.
- If neither route is usable, explain the actual blocker. If Blender is absent, ask whether the user wants help installing it from an official source. Respect local execution permissions and report a denied command accurately.

Read the installed entrypoint's collaboration instructions for delivery evidence. If the user declines required installation, or neither execution route can be made available, preserve the existing assets and explain that assembly is incomplete.

## Build the architectural shell when planned

When planning selects Blender for the shell, use Blender Python or verified MCP capabilities to model it with editable, named structural objects and organize them by level or room. Establish coherent units, floor heights, openings, and placement space before fitting assets. Use reasonable dimensional assumptions when no measurements are supplied; do not claim survey accuracy from a perspective reference. Construct materials and structural detail appropriate to the intended views instead of treating a rough blockout as the final shell.

Preserve the reference's exterior or cutaway presentation and required access through rooms, doors, and stairs. Keep structural geometry distinct from generated furniture and props. A planned hybrid scene does not become complete by substituting primitive placeholders for its required Lux3D assets. Record the local construction script and outputs separately from cloud task records.

For a Lux3D-generated shell, inspect the source model against the reference and agreed constraints, then import it for assembly. Keep it separate from its contents and preserve the source file; do not replace it with a Blender blockout simply to follow the assembly workflow.

## Assemble using the actual tools

Once the required assets are ready, import them into the planned shell or scene using Blender Python or the actual MCP tools. Translate relative positions, orientations, connections, hierarchy, and scale into script operations or tool calls; the user does not need to write tool parameters. Reuse instances for repeated objects where possible, and preserve original versions and unaffected objects. Obtain missing required assets before claiming completion; a collection of separate models is not a finished assembly.

Inspect the actual scene and exports for the required objects, layout, scale, and material resources. For architectural scenes, check that furniture fits its rooms and supporting surfaces, circulation and openings remain usable where requested, and the required contents are visible in the intended views. Use Blender to create lighting, cameras, animation, and renders when needed for the requested result; an asset-only request does not require these extras. Any additional billable Lux3D generation or conversion still follows [Review and approval](review.md). Digital assembly does not automatically guarantee physical fit tolerances or printability.

## Lighting, cameras, and rendering

For stills and shots, set lighting, camera framing, and render settings to match the plan. For camera movement, arrange foreground, subject, and background depth and animate the camera to produce the requested path, occlusion, parallax, and final framing. Judge these effects through the camera view rather than object coordinates alone.

Save the Blender scene and production script before expensive rendering. Choose an available render engine and settings appropriate to the hardware and requested quality. Inspect a low-cost preview or representative frames before the final render; for animation, include the start, end, and important movement or occlusion transitions. Correct visible problems in composition, materials, lighting, clipping, or motion, then render the requested output. This inspection does not require a separate user checkpoint unless the user requested one.

Verify that the final image opens or the video plays, and check its resolution, duration/frame count, and visual content against the plan. A successful render command or a single still does not establish that the requested shot is complete. Keep rendered frames when useful for recovery. If rendering or encoding fails, resume from the saved scene or completed frames; do not regenerate Lux3D assets to repair a local output failure. Preserve usable files and report any unresolved limitation.

## Export and deliver

Export `scene.glb` with its resources embedded for model/scene delivery. Use the delivery contract's `scene` field for both composed scenes and multipart assemblies. Preserve lighting, cameras, animation, and render settings in the Blender working file; do not assume a GLB export or the model preview page reproduces the rendered look or camera motion. Provide the `.blend` file when requested or included in the plan.

Deliver requested rendered images or video as separate files using [Results and delivery](results.md). They are local Blender outputs, not Lux3D generation artifacts or inputs to the existing scene-ingestion contract. A successful scene export does not replace a requested render.

Record exported files, source-asset relationships, and execution evidence according to `core/contracts/scene-delivery.md`. Do not invent missing information. Follow [Results and delivery](results.md) to inspect the files and prepare the unified delivery page. Report missing objects, exports, or evidence accurately, and preserve usable assets.
