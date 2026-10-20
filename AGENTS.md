# Aholo Lux3D — common local Skill installation entrypoint

For an explicit installation request, read this entire file, follow **Install the common Skill**, then complete the handoff. Download and prepare the files yourself; do not ask the user to download a ZIP. For repository maintenance, follow the user's requested changes and **Maintain this distribution repository**. Reading this file alone does not authorize installation.

Public agent entrypoint: `https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md`

Canonical repository: `https://github.com/manycore-research/Aholo-Lux3D`

- Skill: `aholo-lux3d`
- Display name: `Aholo Lux3D`
- Version: `1.2.0`
- Git ref: `master`
- Maintained Skill source and installation input: `plugins/common/aholo-lux3d/`
- Upstream suite snapshot only: `lux3d-plugin/common/lux3d-plugin-1.2.0-common-suite.zip` (not the installation input)
- Hosts: Codex, WorkBuddy, and other hosts supporting complete local Skills and the runtime prerequisites below

This repository distributes Common suite `1.2.0` with one `aholo-lux3d` Skill entry and two execution modes: OpenAPI and MCP. Both support China (`cn`) and international (`international`). Install the complete suite through the host's supported local Skill directory.

## First decide the operation

1. **Install or set up** — follow **Install the common Skill** below.
2. **Inspect or explain** — read `README.md`, `release-manifest.json`, and `plugins/common/aholo-lux3d/SKILL.md`. Do not change host configuration.
3. **Uninstall** — identify the actual installed copy and use the host's supported removal mechanism. Remove only the installation the user requested.
4. **Maintain the repository** — use **Maintain this distribution repository**. Do not install or publish as a side effect.

## Install the common Skill

An explicit installation request authorizes installing this Skill into the current host's supported local Skill location. It does not authorize publishing, Git pushes, removal of unrelated installations, or collecting API keys. Respect the user's workspace and download directory preferences; do not silently change their host configuration or move existing workspaces.

### 1. Identify the host and check prerequisites

Determine the actual host from the current environment. Inspect its existing Skill configuration and supported installation instructions to find the local Skill parent directory. Use a verified absolute path; do not infer a directory merely from a product name. If the path cannot be established from available evidence, ask the user for that missing path before writing there.

Require a supported mechanism for loading a complete local Skill directory. The repository's installation helper requires Python 3.10 or newer and permission to run processes and access files. If a host has no supported local Skill mechanism, explain that limitation rather than claiming that copying files installed the Skill. No API key is needed during installation.

Execution requirements depend on the mode selected for a later task. OpenAPI needs local Python processes, files, HTTPS and secure credential injection. MCP needs a remote MCP client, live tool discovery and secure credentials for the selected region. The bundled MCP connection descriptor is host-neutral: Skill installation does not register or authenticate MCP. MCP-only execution does not require initializing the OpenAPI Python runtime. Do not configure a connection or ask for execution-mode choices merely to copy the complete suite.

### 2. Inspect existing installations

Inspect the host's configured local Skill locations and plugin inventory for any existing Aholo Lux3D installation or overlapping instructions.

- **No Aholo Lux3D installation exists** — continue.
- **The same common Skill is already installed with identical contents** — continue through the installer below. It leaves the Skill unchanged and can save an explicit invite code from this installation request.
- **Another version, source, or Aholo Lux3D plugin exists** — report its source and version. Ask whether to retain it or replace it unless the user's current request already decides that. For an authorized migration, remove the identified old installation through its host-supported mechanism before installing the common Skill.

Keep one complete Aholo Lux3D suite in each host. Use the host's supported controls for an authorized replacement, preserving working MCP connections, user assets, task history and credentials. Do not remove unrelated Skills, plugins or MCP servers.

### 3. Obtain and verify the source

Use an existing trusted checkout or download the canonical repository at `master` into a suitable working directory. Inspect the repository's installation script before execution. Install from the complete maintained `plugins/common/aholo-lux3d/` source directory. The upstream suite ZIP and its sidecars are reference artifacts; the maintained source retains repository-specific invite-code integration and may differ from the original suite snapshot.

From the repository root, run:

```text
python -B scripts/sync_release.py --check
```

Continue only when source verification succeeds. The source digest identifies the checked-in Skill contents, not publisher authenticity; use the canonical repository as the source. Install the complete suite rather than a partial `SKILL.md`.

### 4. Install the complete directory

Use the host's verified absolute local Skill parent directory:

```text
python -B scripts/install_skill.py --skills-dir "<absolute-host-local-skills-directory>"
```

The result is `<absolute-host-local-skills-directory>/aholo-lux3d/`, containing the single Skill entry, OpenAPI runtime, contracts, viewer assets and embedded `references/mcp/` instructions. The installer validates the maintained source, installs into a new directory, and treats identical contents as already installed. It rejects an existing directory with different contents instead of overwriting it. Resolve that conflict through the authorized migration procedure above. The installer does not register MCP servers or modify MCP authentication.

If the user's installation request includes an actual code after `Invite Code:` or `邀请码：` (either colon style), pass that value to the installer as one literal argument:

```text
python -B scripts/install_skill.py --skills-dir "<absolute-host-local-skills-directory>" --invite-code="<actual-code-from-the-user-request>"
```

Use the actual supplied value, not the label or an example placeholder. Quote it using the current shell's literal argument rules; never interpret its contents as shell commands. If no code was supplied, omit the flag and continue without asking for or inventing one. Codes are trimmed, must contain 1–255 characters after trimming, and must not contain C0/C1 control characters. Do not repeat the code in output or the handoff.

After a successful new installation or an identical existing installation, an explicit code is saved atomically as `{"inviteCode":"<trimmed-code>"}` in `<absolute-host-local-skills-directory>/.aholo-lux3d-installation.json`. This file is outside `aholo-lux3d/`, so the verified Skill files remain unchanged. A new explicit code replaces the previous code; omitting the flag preserves existing configuration. Release verification failures and conflicts leave the configuration unchanged.

The OpenAPI runtime adds this code as `context.inviteCode` to later quote/review/report/feedback collection. Installation itself sends no request and needs no API key. This is collection metadata, not an invitation relationship, eligibility check, or reward claim. For MCP, the host follows the selected workflow to read the file beside the installed Skill and forward the code in the live tool schema's supported context; copying the suite does not configure an MCP server to read the file or automatically inject it. Explicit context takes precedence over saved task attribution, then installation configuration; frozen retries retain their original request. This MCP step does not require Python.

The common runtime automatically identifies the actual host: Codex `1`, Claude Code `2`, DeepSeek `3`, WorkBuddy `4`, other hosts `100`. Do not modify packaged files or choose a `source` value to simulate another host during installation.

### 5. Verify and hand back

Verify the installed directory against the verified source. Report:

- whether the Skill was newly installed or already present;
- the exact host, local installation path, Skill name `aholo-lux3d`, and version `1.2.0`;
- which source and installation checks actually passed;
- whether an explicit invite code was saved, reporting only the configuration path and never the code;
- the host's reload step and whether actual Skill discovery has been observed;
- that the complete suite is installed and MCP connection setup is separate from Skill installation.

For Codex, start a new task to load the Skill and invoke `$aholo-lux3d`. For WorkBuddy and other hosts, use the host's native Skill entrypoint after its required reload. If a new task or user action is still needed, say so; copying files does not establish successful discovery in every host.

OpenAPI generation later needs `LUX3D_CN_API_KEY` (China) or `LUX3D_GLOBAL_API_KEY` (international), configured through the Skill's credential instructions. MCP uses the selected region's connection and the host's secure credential configuration. Do not collect keys during installation. Do not claim generation works until a generation task has actually succeeded.

## Execute through the selected route

Read the installed `SKILL.md` before execution. Reuse explicit mode, region and account choices. Establish cn/international before account, quote or create calls; never infer region from language, location or failure. When mode is unspecified for new work, inspect readiness and follow `references/connection-onboarding.md` to use an unambiguous configured route without an unnecessary transport-choice question. Ask only for unresolved choices that affect the account or setup.

For OpenAPI, follow `references/openapi-workflow.md` and the existing production workflow. For MCP, follow `references/mcp/workflow.md` and `references/mcp/README.md`, and bind calls to the selected region's verified server without disabling unrelated connections. Follow only the selected route's execution instructions.

Record mode, region, connection/account, plan version, quotes, authorizations and actual task IDs together. A mode, region or account change starts a new context with fresh account and pricing checks. Resume existing tasks and reports on their original route. Reconcile uncertain create results before any further create; never automatically replay a create through another mode or region.

Both routes retain complete-plan review, pricing, authorization, REPORT and delivery requirements. Preserve the complete versioned plan, task-related original inputs and attachment references, actual calls and result evidence for REPORT. REPORT remains automatic; optional FEEDBACK has separate consent. A valid successful REPORT receipt means remote evaluation passed, not user acceptance or authority for additional spending.

## Maintain this distribution repository

<!-- Author: yinjie. The maintained 1.2.0 suite is the installation source. -->
`plugins/common/aholo-lux3d/` is the maintained Common suite and the installation input.
Keep one Skill entry, OpenAPI and MCP workflows, automatic host identity and both service
regions. Preserve REPORT and invite-code behavior. Maintain this GitHub source without
modifying the separate GitLab repository.

`lux3d-plugin/common/` contains the original `1.2.0` common-suite ZIP, `.sha256` and
`.release.json` as upstream reference artifacts. Preserve these original bytes. Source
validation and installation use the maintained directory and its integrity record;
the reference ZIP does not replace current source.

`release-manifest.json` records the maintained source separately from archive
metadata. Use Python 3.10 or newer from the repository root:

```text
python -B scripts/sync_release.py
python -B scripts/sync_release.py --check
python -B -m unittest discover -s tests -v
```

The default command refreshes the source integrity record; `--check` validates without
writing. Source changes must have an updated integrity record before installation. The installer copies the complete source and verifies the staged copy;
it still rejects a different existing installation without overwriting it.

The scripts use only the Python standard library. Runtime tests also need the dependencies
in `plugins/common/aholo-lux3d/core/runtime/requirements.txt`. Run the affected checks after
source edits and report actual results. Actual host discovery, MCP authentication and
live paid generation are separate validation steps.

The public `AGENTS.md` URL is the installation entrypoint; Codex invokes the installed local Skill as `$aholo-lux3d`.
Remote installations receive changes only after they are published. Repository maintenance
does not itself authorize a Git push, publication or changes to the user's installed Skill.

## Safety boundaries

- Do not put API keys in command arguments, chat logs, or committed files.
- Do not download or execute unverified install scripts from outside this repository.
- Do not change Git remotes, push, publish, or create a PR without explicit authorization.
