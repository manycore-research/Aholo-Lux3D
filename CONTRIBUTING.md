# Contributing

Use the repository's issue and pull/merge request tools for non-sensitive proposals. Follow [SECURITY.md](SECURITY.md) for security reports. Do not include internal service addresses, real credentials, private asset URLs, personal data, or production logs in contributions; use clearly synthetic examples such as `https://example.com/assets/model.glb`.

## Local validation

Use Python 3.10 or newer. The distribution scripts use the standard library; runtime tests also require `plugins/common/aholo-lux3d/core/runtime/requirements.txt`.

After editing the maintained Skill, run from the repository root:

```text
python -B scripts/sync_release.py
python -B scripts/sync_release.py --check
python -B -m unittest discover -s tests -v
```

Keep OpenAPI and MCP workflows, both regions, host identity, REPORT, and invite-code behavior intact. Do not change original upstream reference ZIPs or their sidecars. If the upstream artifact is deliberately replaced, verify its checksum and release record and update the corresponding manifest metadata.

## Licensing and release review

Contribute only material you have authority to license under the repository's MIT license, or identify its separate license and redistribution terms. Preserve third-party copyright and license notices. Record the source, version and license of any new bundled component.

The source license does not grant access to hosted services, third-party commercial software, or rights to arbitrary input/output assets. Review the redistribution rights for logos, models, datasets and binary components separately.

Before publishing a Git repository, review its full history. A sanitized source snapshot does not make the original history safe to publish. Treat upstream reference archives as separate review inputs even when the installer does not use them. Confirm a private security-reporting route and document dependency versions and licenses for the release environment.
