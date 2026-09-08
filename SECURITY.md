# Security and reporting

The skill is an instruction layer, not a sandbox, authorization system or security scanner. The hosting agent's permissions remain authoritative. Do not treat a model's GREEN as independent certification.

Do not include secrets, real customer records or personal filesystem paths in public reports. For a vulnerability, share a minimal synthetic reproduction and describe the affected version and boundary. Public, non-sensitive bugs can be filed at https://github.com/Cheer12936/ThinStack/issues. No private security reporting channel is currently configured; do not post exploitable details, credentials or personal data publicly.

Installer operations are limited to a named ts-code directory under the explicitly supplied skills root. Updates/uninstalls archive old content; they do not recursively delete user directories.
