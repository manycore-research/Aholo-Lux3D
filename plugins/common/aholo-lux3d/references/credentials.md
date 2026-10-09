# Common credential setup

Use the user's selected `cn` or `international` region, including a region
previously chosen in the current task context. Ask for the region only when
it is not yet known. Never infer a different region from language, location or
a network failure, and never retry a failed request against another region.

Direct the user to the selected site's key page:
[China](https://labs.aholo3d.cn/api-keys?from=lux3d) or
[international](https://labs.aholo3d.com/api-keys?from=lux3d). Have them store the key in the
host's secure credential settings or a private local credential store that can
inject it into the operation's child process. Do not ask them to paste a key in
chat. Keep keys out of host metadata, command arguments, projects,
version control, quote files, logs and deliverables.

| Selected region | Process environment variable | Service origin |
| --- | --- | --- |
| `cn` | `LUX3D_CN_API_KEY` | `https://api.aholo3d.cn` |
| `international` | `LUX3D_GLOBAL_API_KEY` | `https://api.aholo3d.com` |

The bundled clients use the raw key in `Authorization`; do not prepend
`Bearer`. International HTTP calls use `/global`, while quote plans keep the
original canonical `/lux3d/v1/...` paths. Bind the credential to the selected
service; never send it with asset downloads or expose signed resource URLs.

When an existing private credential file is available, read it as data and
inject the latest selected key for that process. Do not alter a shared process's
global environment to switch concurrent users or accounts. The CLI reads the
region-specific environment variable, not arbitrary host credential files.
If the host cannot inject secrets securely, explain that missing capability and
pause API operations while continuing independent planning or local work.

Verify setup with the installed `scripts/commerce.py balance --region <region>`
command. Host identity is resolved automatically from native session metadata
or the host agent's automatically supplied `--host-name` / `LUX3D_HOST_NAME`.
No user-created binding, profile choice or source flag is required. Missing or
rejected credentials require checking the selected key and region. Network
failures do not establish that a key is invalid. On a key or account change,
refresh account facts and all applicable quotes before resuming; do not transfer
approval to different work.

Account setup and queries do not require project files. Honor the user's chosen
drive for any new local configuration or cache location.
