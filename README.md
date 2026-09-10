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

Open [the install page](./index.html), copy the prompt, paste it into a Codex task.

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
AGENTS.md                          Instructions Codex follows when installing
index.html                         Human install page
lux3d-plugin/codex/*.tar.gz        OpenAI portal archive only, not the user path
```
