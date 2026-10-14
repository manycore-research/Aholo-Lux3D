# Agent installation prompt

This repository distributes the common suite `aholo-lux3d`, version `1.2.0`, for Codex, WorkBuddy, and other compatible hosts. One local Skill entry supports both OpenAPI and MCP workflows.

Paste this into the host where you want to install the Skill:

```text
Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D as a local Skill in the current host.
```

The agent checks the actual host's supported Skill directory and existing installations, obtains and verifies the repository, and installs the complete suite from `plugins/common/aholo-lux3d/`. The installation helper requires Python 3.10 or newer. You do not need to download a ZIP or supply an API key to install. The original `1.2.0` suite ZIP provides upstream provenance; installation uses maintained source.

If the website supplied an invite code, append `Invite Code: <your-actual-invite-code>` or `邀请码：<实际邀请码>` to the installation request, replacing the placeholder with that code. Leave this suffix out when you have no code; the agent must not ask for or invent one.

The agent passes the supplied code through `--invite-code` and saves it outside the Skill at `<host-local-skills-directory>/.aholo-lux3d-installation.json`. An explicit new code can update an identical installation; a request without a code preserves existing configuration. Later OpenAPI quote/review/report/feedback collection includes `context.inviteCode`. This records installation attribution only; it does not bind an invitation relationship or grant rewards. Installation makes no Lux3D API call, and the agent must not repeat the code in its response.

For MCP, the host reads and forwards the saved code according to the selected workflow and the live tool schema's supported context. This follows host instructions rather than the OpenAPI runtime's automatic injection; explicit context and saved task attribution take precedence over installation configuration, and frozen retries keep their original request.

After installation, reload Skills or start a new task according to the host's requirements. In a new Codex task, invoke:

```text
$aholo-lux3d Create a verified 3D asset from this brief and deliver an offline preview.
```

WorkBuddy and other hosts use their native Skill entrypoint. All compatible hosts receive the same files, with automatic detection of the actual host. Do not select a `source` value manually during installation.

Before account, quote or create calls, the agent reuses your established execution mode (OpenAPI or MCP) and region (China or international), or asks for missing choices. OpenAPI uses the bundled Python runtime. MCP uses the embedded workflow and the selected region's connection; installing the Skill does not register or authenticate an MCP server. MCP execution does not require initializing the OpenAPI runtime.

A mode, region or account change starts a new execution context with fresh account and pricing checks. Existing tasks and reports resume on their original route, and uncertain create results must be reconciled before another create. Both routes retain planning, authorization, automatic REPORT and delivery requirements.

The public `AGENTS.md` URL is the installation entrypoint for the complete Common suite. Keep one Aholo Lux3D installation per host. To replace existing content, follow the installation checks in `AGENTS.md`; the installer rejects different existing content without overwriting it.

For repository maintenance, use the common release synchronization commands in `README.md` and `AGENTS.md`. Local package checks do not establish publication, Skill discovery in all hosts, or live generation acceptance.
