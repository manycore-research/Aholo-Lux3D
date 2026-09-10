# Model assembly

For scene composition, multipart assembly, or layout changes to existing models, use local Blender or an available Blender MCP. The agent translates the user's spatial relationships and the plan's layout into a Blender Python script or actual MCP calls. Lux3D supplies the generated assets; the plugin does not implement a scene builder or copy or pin an MCP schema.

## Check the environment and tools

Check for a usable Blender executable or an available Blender MCP. Distinguish an absent application, a stopped application, and a missing MCP connection.

- For local Blender, resolve its executable from the installed application or `PATH` and check `--version` and `--help`. On macOS, the usual application executable is `/Applications/Blender.app/Contents/MacOS/Blender`; verify that it exists. Use the installed version's Python API for import, object transforms, scene inspection, and export.
- Run a task-local Python script with the actual executable, for example `"<blender-executable>" --background --factory-startup --python-exit-code 1 --python "<assembly.py>"`. This starts a separate background process, requires no open Blender window or MCP connection, and leaves the user's open document alone. Use Blender's embedded Python for `bpy`, not the Lux3D API environment. Open the GUI only when needed for the requested interaction or inspection; the user need not launch Blender manually.
- If using MCP, discover the available tools and read their actual schemas. Do not guess tool names or parameters. If MCP is missing or disconnected, use local Blender when available instead of stopping or requiring MCP setup.
- If neither route is usable, explain the actual blocker. If Blender is absent, ask whether the user wants help installing it from an official source. Respect local execution permissions and report a denied command accurately.

Read the installed entrypoint's collaboration instructions for delivery evidence. If the user declines required installation, or neither execution route can be made available, preserve the existing assets and explain that assembly is incomplete.

## Assemble using the actual tools

Once the required assets are ready, import them using Blender Python or the actual MCP tools. Translate relative positions, orientations, connections, hierarchy, and scale into script operations or tool calls; the user does not need to write tool parameters. Reuse instances for repeated objects where possible, and preserve original versions and unaffected objects. Obtain missing required assets before claiming completion; a collection of separate models is not a finished assembly.

Inspect the actual scene and exports for the required objects, layout, scale, and material resources. Blender only handles assembly here: do not create lighting, cameras, or renders. Any additional billable Lux3D generation or conversion still follows [Review and approval](review.md). Digital assembly does not automatically guarantee physical fit tolerances or printability.

## Export and deliver

Export `scene.glb` with its resources embedded. Also provide a `.blend` file if requested. Use the delivery contract's `scene` field for both composed scenes and multipart assemblies.

Record exported files, source-asset relationships, and execution evidence according to `core/contracts/scene-delivery.md`. Do not invent missing information. Follow [Results and delivery](results.md) to inspect the files and prepare the unified delivery page. Report missing objects, exports, or evidence accurately, and preserve usable assets.
