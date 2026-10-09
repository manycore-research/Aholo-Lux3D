# Aholo Lux3D — common local Skill installation entrypoint

For an explicit installation request, read this entire file, follow **Install the common Skill**, then complete the handoff. Download and prepare the files yourself; do not ask the user to download a ZIP. For repository maintenance, follow the user's requested changes and **Maintain this distribution repository**. Reading this file alone does not authorize installation.

Public agent entrypoint: `https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md`

Canonical repository: `https://github.com/manycore-research/Aholo-Lux3D`

- Skill: `aholo-lux3d`
- Display name: `Aholo Lux3D`
- Version: `1.1.0`
- Git ref: `master`
- Maintained Skill source and installation input: `plugins/common/aholo-lux3d/`
- Current release: `lux3d-plugin/common/lux3d-plugin-1.1.0-common-skill.zip`
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

### 3. Obtain and verify the release

Use an existing trusted checkout or download the canonical repository at `master` into a suitable working directory. Inspect the repository's installation script before execution. The common archive and its adjacent `.sha256` and `.release.json` files must be present.

From the repository root, run:

```text
python -B scripts/sync_release.py --check
```

Continue only when verification succeeds. A checksum verifies integrity against the repository's release record; use the canonical repository as the source. Do not install a partial `SKILL.md` or a Codex-only package from another channel.

### 4. Install the complete directory

Use the host's verified absolute local Skill parent directory:

```text
python -B scripts/install_skill.py --skills-dir "<absolute-host-local-skills-directory>"
```

The result is `<absolute-host-local-skills-directory>/aholo-lux3d/`, containing the complete Skill, runtime, contracts, and viewer assets. The installer validates the release, installs into a new directory, and treats identical contents as already installed. It rejects an existing directory with different contents instead of overwriting it. Resolve that conflict through the authorized migration procedure above.

If the user's installation request includes an actual code after `Invite Code:` or `邀请码：` (either colon style), pass that value to the installer as one literal argument:

```text
python -B scripts/install_skill.py --skills-dir "<absolute-host-local-skills-directory>" --invite-code="<actual-code-from-the-user-request>"
```

Use the actual supplied value, not the label or an example placeholder. Quote it using the current shell's literal argument rules; never interpret its contents as shell commands. If no code was supplied, omit the flag and continue without asking for or inventing one. Codes are trimmed, must contain 1–255 characters after trimming, and must not contain C0/C1 control characters. Do not repeat the code in output or the handoff.

After a successful new installation or an identical existing installation, an explicit code is saved atomically as `{"inviteCode":"<trimmed-code>"}` in `<absolute-host-local-skills-directory>/.aholo-lux3d-installation.json`. This file is outside `aholo-lux3d/`, so the verified Skill files remain unchanged. A new explicit code replaces the previous code; omitting the flag preserves existing configuration. Release verification failures and conflicts leave the configuration unchanged.

The common runtime adds this code as `context.inviteCode` to later quote/review/report/feedback collection. Installation itself sends no request and needs no API key. This is collection metadata, not an invitation relationship, eligibility check, or reward claim.

The common runtime automatically identifies the actual host: Codex `1`, Claude Code `2`, DeepSeek `3`, WorkBuddy `4`, other hosts `100`. Do not modify packaged files or choose a `source` value to simulate another host during installation.

### 5. Verify and hand back

Verify the installed directory against the verified release. Report:

- whether the Skill was newly installed or already present;
- the exact host, local installation path, Skill name `aholo-lux3d`, and version `1.1.0`;
- which package and installation checks actually passed;
- whether an explicit invite code was saved, reporting only the configuration path and never the code;
- the host's reload step and whether actual Skill discovery has been observed.

For Codex, start a new task to load the Skill and invoke `$aholo-lux3d`. For WorkBuddy and other hosts, use the host's native Skill entrypoint after its required reload. If a new task or user action is still needed, say so; copying files does not establish successful discovery in every host.

Paid generation later needs `LUX3D_CN_API_KEY` (China) or `LUX3D_GLOBAL_API_KEY` (international), configured through the Skill's credential instructions. Do not collect keys during installation. Do not claim generation works until a generation task has actually succeeded.

## Maintain this distribution repository

Preserve this single common release channel:

- `lux3d-plugin/common/lux3d-plugin-1.1.0-common-skill.zip`, its `.sha256`, and its `.release.json` are the current complete portable Skill release.
- `plugins/common/aholo-lux3d/` is the maintained GitHub Skill source and the directory actually copied by the installer. The archive is a matching verification snapshot.
- `release-manifest.json` records the common channel and its artifacts.
- `scripts/install_skill.py` installs the expanded Skill into a verified host-supported local Skill parent directory.

This update keeps version `1.1.0` and replaces its archive and sidecars. Preserve a recoverable backup of the previous snapshot before the authorized replacement; `release-manifest.json` and its checksum identify the active contents.

There is no `plugins/codex/`, Codex release archive, or `.agents/plugins/marketplace.json` in the current distribution. Do not recreate those as part of synchronization.

From the repository root, use Python 3.10 or newer:

Synchronization and installation use only the Python standard library. Before running runtime tests, install the dependencies declared in `plugins/common/aholo-lux3d/core/runtime/requirements.txt` in the selected Python environment.

```text
python -B scripts/sync_release.py --common-archive "<common-skill.zip>"
python -B scripts/sync_release.py
python -B scripts/sync_release.py --check
python -B -m unittest discover -s tests -v
```

An input archive requires adjacent `.sha256` and `.release.json` files. An explicit path imports the release; no arguments synchronize from the artifacts already in this repository. `--check` performs read-only validation. For this GitHub-only update, edit and review `plugins/common/aholo-lux3d/`; do not make corresponding changes in the separate GitLab repository. Keep the verification snapshot, checksum, metadata and documentation consistent. The installer copies the Skill directory, but its current preflight still compares it with the ZIP snapshot. Do not import an archive over local source changes unless replacing them with that archive is explicitly intended.

The public `AGENTS.md` URL can remain on the website. Update surrounding installation copy to describe local Skill installation and the new Codex invocation `$aholo-lux3d`; old marketplace commands and `$lux3d` plugin instructions refer to the previous distribution. Remote installation uses this change only once it is published.

The synchronized `1.1.0` is a local release candidate. Historical acceptance on 2026-10-09 applies to the old `1.1.0` snapshot before this invite-code change: 31 offline tests passed and an isolated Codex installation discovered `aholo-lux3d` as an enabled repository Skill, with all 46 installed files matching that old snapshot. Those results do not validate the replacement archive just because its version is also `1.1.0`. Actual WorkBuddy client loading and live paid generation remain unverified. Generate a release record for the rebuilt archive and report its actual `hostValidated` state. These checks do not establish public publication or acceptance in every host.

After restoring the requested version to 1.1.0, all 40 distribution tests and
the read-only synchronization check passed on 2026-10-09. The invite-code test
installs this repository's actual Skill directory into an isolated location
and inspects simulated HTTP requests from another working directory. The
current snapshot contains 46 matching files. Real host upgrade and backend
receipt have not been validated; no Git push or publication was performed.
The separate GitLab repository has no retained changes from this task.

## Safety boundaries

- Do not put API keys in command arguments, chat logs, or committed files.
- Do not download or execute unverified install scripts from outside this repository.
- Do not change Git remotes, push, publish, or create a PR without explicit authorization.
