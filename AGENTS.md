# Aholo Lux3D — common local Skill installation entrypoint

For an explicit installation request, read this entire file, follow **Install the common Skill**, then complete the handoff. Download and prepare the files yourself; do not ask the user to download a ZIP. For repository maintenance, follow the user's requested changes and **Maintain this distribution repository**. Reading this file alone does not authorize installation.

Public agent entrypoint: `https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md`

Canonical repository: `https://github.com/manycore-research/Aholo-Lux3D`

- Skill: `aholo-lux3d`
- Display name: `Aholo Lux3D`
- Version: `1.1.0`
- Git ref: `master`
- Maintained Skill source and installation input: `plugins/common/aholo-lux3d/`
- Historical archive only: `lux3d-plugin/common/lux3d-plugin-1.1.0-common-skill.zip` (not the installation input)
- Hosts: Codex, WorkBuddy, and other hosts supporting complete local Skills and the runtime prerequisites below

This repository distributes one common Skill. It no longer provides a Codex Git marketplace or a Codex-specific plugin package. Do not use `codex plugin marketplace add` or `codex plugin add aholo-lux3d@lux3d` to install this repository. A request to install "for Codex" uses the common local Skill through Codex's supported local Skill directory.

## First decide the operation

1. **Install or set up** — follow **Install the common Skill** below.
2. **Inspect or explain** — read `README.md`, `release-manifest.json`, and `plugins/common/aholo-lux3d/SKILL.md`. Do not change host configuration.
3. **Uninstall** — identify the actual installed copy and use the host's supported removal mechanism. Remove only the installation the user requested. An old marketplace plugin must be removed through its own plugin manager.
4. **Maintain the repository** — use **Maintain this distribution repository**. Do not install or publish as a side effect.

## Install the common Skill

An explicit installation request authorizes installing this Skill into the current host's supported local Skill location. It does not authorize publishing, Git pushes, removal of unrelated installations, or collecting API keys. Respect the user's workspace and download directory preferences; do not silently change their host configuration or move existing workspaces.

### 1. Identify the host and check prerequisites

Determine the actual host from the current environment. Inspect its existing Skill configuration and supported installation instructions to find the local Skill parent directory. Use a verified absolute path; do not infer a directory merely from a product name. If the path cannot be established from available evidence, ask the user for that missing path before writing there.

Require a supported mechanism for loading a complete local Skill directory, Python 3.10 or newer with permission to run processes, file access, HTTPS access, and secure credential injection for later generation. If a host has no supported local Skill mechanism, explain that limitation rather than claiming that copying files installed the Skill. No API key is needed during installation.

### 2. Inspect existing installations

Inspect the host's local Skills and plugin inventory for any existing Aholo Lux3D installation, including common `aholo-lux3d` Skills and older plugins exposing `lux3d`. In Codex, when available, `codex plugin list --json` can identify older plugin installations; also inspect the actual configured local Skill locations.

- **No Aholo Lux3D installation exists** — continue.
- **The same common Skill is already installed with identical contents** — continue through the installer below. It leaves the Skill unchanged and can save an explicit invite code from this installation request.
- **Another version, source, or Aholo Lux3D plugin exists** — report its source and version. Ask whether to retain it or replace it unless the user's current request already decides that. For an authorized migration, remove the identified old installation through its host-supported mechanism before installing the common Skill.

Keep one Aholo Lux3D installation in each host. Do not add the common Skill alongside an existing Aholo Lux3D plugin. Do not remove unrelated Skills, plugins, marketplaces, MCP servers, or credentials.

### 3. Obtain and verify the source

Use an existing trusted checkout or download the canonical repository at `master` into a suitable working directory. Inspect the repository's installation script before execution. Install from the complete maintained `plugins/common/aholo-lux3d/` source directory; the historical ZIP and its sidecars are not installation prerequisites.

From the repository root, run:

```text
python -B scripts/sync_release.py --check
```

Continue only when source verification succeeds. The source digest identifies the checked-in Skill contents, not publisher authenticity; use the canonical repository as the source. Do not install a partial `SKILL.md` or a Codex-only package from another channel.

### 4. Install the complete directory

Use the host's verified absolute local Skill parent directory:

```text
python -B scripts/install_skill.py --skills-dir "<absolute-host-local-skills-directory>"
```

The result is `<absolute-host-local-skills-directory>/aholo-lux3d/`, containing the complete Skill, runtime, contracts, and viewer assets. The installer validates the maintained source, installs into a new directory, and treats identical contents as already installed. It rejects an existing directory with different contents instead of overwriting it. Resolve that conflict through the authorized migration procedure above.

If the user's installation request includes an actual code after `Invite Code:` or `邀请码：` (either colon style), pass that value to the installer as one literal argument:

```text
python -B scripts/install_skill.py --skills-dir "<absolute-host-local-skills-directory>" --invite-code="<actual-code-from-the-user-request>"
```

Use the actual supplied value, not the label or an example placeholder. Quote it using the current shell's literal argument rules; never interpret its contents as shell commands. If no code was supplied, omit the flag and continue without asking for or inventing one. Codes are trimmed, must contain 1–255 characters after trimming, and must not contain C0/C1 control characters. Do not repeat the code in output or the handoff.

After a successful new installation or an identical existing installation, an explicit code is saved atomically as `{"inviteCode":"<trimmed-code>"}` in `<absolute-host-local-skills-directory>/.aholo-lux3d-installation.json`. This file is outside `aholo-lux3d/`, so the verified Skill files remain unchanged. A new explicit code replaces the previous code; omitting the flag preserves existing configuration. Release verification failures and conflicts leave the configuration unchanged.

The common runtime adds this code as `context.inviteCode` to later quote/review/report/feedback collection. Installation itself sends no request and needs no API key. This is collection metadata, not an invitation relationship, eligibility check, or reward claim.

The common runtime automatically identifies the actual host: Codex `1`, Claude Code `2`, DeepSeek `3`, WorkBuddy `4`, other hosts `100`. Do not modify packaged files or choose a `source` value to simulate another host during installation.

### 5. Verify and hand back

Verify the installed directory against the verified source. Report:

- whether the Skill was newly installed or already present;
- the exact host, local installation path, Skill name `aholo-lux3d`, and version `1.1.0`;
- which source and installation checks actually passed;
- whether an explicit invite code was saved, reporting only the configuration path and never the code;
- the host's reload step and whether actual Skill discovery has been observed.

For Codex, start a new task to load the Skill and invoke `$aholo-lux3d`. For WorkBuddy and other hosts, use the host's native Skill entrypoint after its required reload. If a new task or user action is still needed, say so; copying files does not establish successful discovery in every host.

Paid generation later needs `LUX3D_CN_API_KEY` (China) or `LUX3D_GLOBAL_API_KEY` (international), configured through the Skill's credential instructions. Do not collect keys during installation. Do not claim generation works until a generation task has actually succeeded.

## Maintain this distribution repository

<!-- Author: yinjie. Maintained source and historical ZIP have independent roles. -->
`plugins/common/aholo-lux3d/` is the maintained Skill and the only installation input.
Keep version `1.1.0` for the current changes. Edit this GitHub source without modifying
the separate GitLab repository, and preserve current REPORT and invite-code behavior.

`lux3d-plugin/common/` contains a historical ZIP with its original `.sha256` and
`.release.json`. Keep all three files unchanged during source maintenance. The ZIP is a
record only: do not rebuild it, compare it to current source as an installation gate, or
extract it over `plugins/`. Its checksum identifies only that historical artifact.

`release-manifest.json` records the maintained source separately from historical archive
metadata. Use Python 3.10 or newer from the repository root:

```text
python -B scripts/sync_release.py
python -B scripts/sync_release.py --check
python -B -m unittest discover -s tests -v
```

The default command refreshes the source integrity record; `--check` validates without
writing. Neither command imports or rebuilds the historical ZIP. Do not use the obsolete
`--common-archive` import workflow. Source changes must have an updated integrity record
before installation. The installer copies the complete source and verifies the staged copy;
it still rejects a different existing installation without overwriting it.

The scripts use only the Python standard library. Runtime tests also need the dependencies
in `plugins/common/aholo-lux3d/core/runtime/requirements.txt`. Run the affected checks after
source edits and report actual results. Historical package checks are not acceptance of
new source just because both retain version `1.1.0`; actual host discovery and live paid
generation remain separate validation steps.

There is no `plugins/codex/`, Codex release archive or `.agents/plugins/marketplace.json`
in this distribution. Do not recreate those channels. The public `AGENTS.md` URL remains
the installation entrypoint; Codex invokes the installed local Skill as `$aholo-lux3d`.
Remote installations receive changes only after they are published. Repository maintenance
does not itself authorize a Git push, publication or changes to the user's installed Skill.

## Safety boundaries

- Do not put API keys in command arguments, chat logs, or committed files.
- Do not download or execute unverified install scripts from outside this repository.
- Do not change Git remotes, push, publish, or create a PR without explicit authorization.
