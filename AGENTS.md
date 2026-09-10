# Aholo Lux3D for Codex — agent installation entrypoint

The user asked you to install Aholo Lux3D for Codex. Read this entire file, follow **Install into Codex**, then complete the handoff. Do not ask the user to download a zip.

Canonical repository: `https://github.com/manycore-research/Aholo-Lux3D`

- Marketplace: `lux3d`
- Plugin: `aholo-lux3d`
- Display name: `Aholo Lux3D`
- Stable selector: `aholo-lux3d@lux3d`
- Plugin version: `0.1.0`
- Git source: `manycore-research/Aholo-Lux3D`
- Git ref: `master`
- Host: Codex Desktop / Codex CLI

This plugin does not register an MCP server. After install, a **new Codex task** is required. Invoke with `$lux3d` or `@aholo-lux3d`.

## First decide the operation

Choose exactly one lane:

1. **Install or set up** — follow "Install into Codex" below.
2. **Inspect or explain** — read `README.md`, `.agents/plugins/marketplace.json`, and `plugins/codex/aholo-lux3d/.codex-plugin/plugin.json`. Do not change configuration.
3. **Uninstall** — `codex plugin remove aholo-lux3d@lux3d`, then optionally `codex plugin marketplace remove lux3d` if no other plugins use that marketplace.

Do not copy plugin files into a Codex home directory. Do not treat `lux3d-plugin/codex/*.tar.gz` as the user install path; that archive is only for the OpenAI plugin portal.

## Install into Codex

An explicit request to install or set up authorizes changes to the user's Codex plugin configuration. It does not authorize Git pushes, publishing, deleting unrelated plugins, or collecting API keys unless the user then asks to generate assets.

### 1. Preflight

```bash
LUX3D_PLUGIN_SOURCE="manycore-research/Aholo-Lux3D"
codex --version
git ls-remote https://github.com/manycore-research/Aholo-Lux3D.git master
```

Require a Codex CLI that supports `codex plugin marketplace` (0.121.0 or newer; prefer 0.144.6+). If `codex` is missing, tell the user to install Codex CLI / ChatGPT desktop first. If `git ls-remote` returns 404, the repository is private or the network cannot reach GitHub; stop and report that the marketplace source must be a public Git repo.

### 2. Inspect before mutating

```bash
codex plugin marketplace list --json
codex plugin list --json
```

If `aholo-lux3d@lux3d` is already installed at version `0.1.0`, do not reinstall it. If marketplace `lux3d` exists but points at a different source, stop and report the name collision. Never remove or overwrite unrelated marketplaces, plugins, MCP servers, or auth state.

### 3. Install the plugin

```bash
codex plugin marketplace add "$LUX3D_PLUGIN_SOURCE" --ref master --json
codex plugin add aholo-lux3d@lux3d --json
```

`alreadyAdded: true` is success.

### 4. Verify

```bash
codex plugin list --json
```

Required evidence:

- plugin id `aholo-lux3d@lux3d`
- installed version `0.1.0`
- marketplace name `lux3d`

### 5. Hand back

Report:

- whether installation was new or already present
- installed plugin id and version
- that a **new Codex task** is needed to load the plugin snapshot
- that the user should invoke `$lux3d` (or `@aholo-lux3d`) in the new task
- that paid generation later needs `LUX3D_CN_API_KEY` (cn) or `LUX3D_GLOBAL_API_KEY` (international) in the environment; do not collect keys during install

Do not claim generation works until a task has actually been submitted.

## Safety boundaries

- Do not put API keys in command arguments, chat logs, or committed files.
- Do not download or execute unverified install scripts from outside this repository.
- Do not change Git remotes, push, publish, or create a PR without explicit authorization.
