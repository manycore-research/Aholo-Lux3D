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
/goal Read https://manycore-research.github.io/Aholo-Lux3D/codex-plugin/
```

Human landing page: [docs/index.html](./docs/index.html)

Direct CLI:

```bash
codex plugin marketplace add manycore-research/Aholo-Lux3D --ref master
codex plugin add aholo-lux3d@lux3d
```

Then start a **new** Codex task and run `$lux3d`.

This repository must stay **public**. `codex plugin marketplace add` clones GitHub. A private repo will 404 for other users.

GitHub Pages: Settings → Pages → Deploy from branch `master` / folder `/docs`.

## Layout

```text
.agents/plugins/marketplace.json   Codex marketplace catalog
plugins/codex/aholo-lux3d/         Installable plugin payload
AGENTS.md                          Canonical agent install guide
docs/index.html                    Human landing (copy the /goal command)
docs/codex-plugin/                 Agent entrypoint Codex reads
lux3d-plugin/codex/*.tar.gz        OpenAI portal archive only
```
