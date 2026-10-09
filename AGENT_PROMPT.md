# Agent installation prompt

This repository distributes the common local Skill `aholo-lux3d`, version `1.1.0`, for Codex, WorkBuddy, and other compatible hosts.

Paste this into the host where you want to install the Skill:

```text
Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D as a local Skill in the current host.
```

The agent checks the actual host's supported Skill directory and existing installations, obtains and verifies the repository, and installs the complete common Skill. You do not need to download a ZIP or supply an API key to install.

If the website supplied an invite code, append `Invite Code: <your-actual-invite-code>` or `邀请码：<实际邀请码>` to the installation request, replacing the placeholder with that code. Leave this suffix out when you have no code; the agent must not ask for or invent one.

The agent passes the supplied code through `--invite-code` and saves it outside the Skill at `<host-local-skills-directory>/.aholo-lux3d-installation.json`. An explicit new code can update an identical installation; a request without a code preserves existing configuration. Later quote/review/report/feedback collection includes `context.inviteCode`. This records installation attribution only; it does not bind an invitation relationship or grant rewards. Installation makes no Lux3D API call, and the agent must not repeat the code in its response.

After installation, reload Skills or start a new task according to the host's requirements. In a new Codex task, invoke:

```text
$aholo-lux3d Create a verified 3D asset from this brief and deliver an offline preview.
```

WorkBuddy and other hosts use their native Skill entrypoint. All compatible hosts receive the same files, with automatic detection of the actual host. Do not select a `source` value manually during installation.

The existing public `AGENTS.md` URL remains valid as an installation entrypoint. A previous prompt asking to install "for Codex" now resolves to this common local Skill. This repository no longer supplies a Codex Git marketplace or a separate Codex plugin; remove the old marketplace commands and `$lux3d` invocation from accompanying website instructions. Published marketplace plugins are managed separately.

Use one Aholo Lux3D installation per host. When migrating an older Skill or plugin, follow the existing-installation checks in `AGENTS.md`; the local installer rejects different existing content rather than overwriting it.

For repository maintenance, use the common release synchronization commands in `README.md` and `AGENTS.md`. Local package checks do not establish publication, Skill discovery in all hosts, or live generation acceptance.
