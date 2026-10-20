# Security policy

## Reporting a vulnerability

Do not post credentials, private asset URLs, personal data, or exploit details in public issues or pull requests. Use a private reporting channel verified by the repository maintainers. If the repository offers private vulnerability reporting, use its Security tab; otherwise request a private contact from a maintainer without disclosing sensitive details.

A dedicated private reporting address and response-time commitment have not yet been established in this repository. Maintainers should confirm the reporting route before a public release; this document does not claim that private reporting is enabled on any hosting service.

Include the affected version or commit, impact, a minimal sanitized reproduction, and relevant redacted logs. Revoke exposed credentials through the service provider and remove sensitive data from shared artifacts.

## Scope and data handling

The maintained local Skill, installer, and bundled viewer are the repository's security-reporting scope. Hosted generation services and host applications have separate operators and policies. No support lifetime or security-update service level is promised here.

Configure credentials through the Skill's credential instructions; never commit credentials or include them in command arguments. Task reports and delivery bundles can contain prompts, account context, original inputs and asset URLs. Review and redact these artifacts before sharing them publicly. Installation does not authorize paid generation.

Before publication, inspect both the current tree and all history being published, as well as ZIP archives and generated assets. Deleting a file from the current tree does not remove it from Git history.
