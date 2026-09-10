# Aholo Lux3D

Codex plugin marketplace for [Aholo Lux3D](https://labs.aholo3d.com). Users install from this Git repo. They do not download a zip.

| Field | Value |
| --- | --- |
| Marketplace | `lux3d` |
| Plugin | `aholo-lux3d` |
| Selector | `aholo-lux3d@lux3d` |
| Version | `0.1.0` |
| Branch | `master` |

## For users

Paste this into a Codex task:

```text
/goal Read https://lux3d.aholo3d.com/lux3d/codex-plugin/ to install Aholo Lux3D for Codex and set up a new task for me.
```

Direct CLI:

```bash
codex plugin marketplace add manycore-research/Aholo-Lux3D --ref master
codex plugin add aholo-lux3d@lux3d
```

Then start a **new** Codex task and run `$lux3d`.

This repository must stay **public**. `codex plugin marketplace add` clones GitHub. A private repo will 404 for other users.

## Layout

```text
.agents/plugins/marketplace.json   Codex marketplace catalog
plugins/codex/aholo-lux3d/         Installable plugin payload
AGENTS.md                          Canonical agent install guide
docs/codex-plugin/                 Agent entrypoint Codex reads
docs/lux3d/codex-plugin/           Production agent entrypoint
lux3d-plugin/codex/*.tar.gz        OpenAI portal archive only
```
