# Contributing

Prefer evidence-backed corrections over new universal rules. Describe the concrete failure, minimal reproduction, intended boundary and observed model behavior. Do not require one exact coding strategy, test count or depth when several choices satisfy risk and acceptance.

Keep SKILL.md as the control plane. Reuse a relevant reference rather than repeating rules. Do not add fixed model names, personal paths, credentials or product-specific assumptions to the core.

Run python tools/validate.py and python -m unittest discover -s tests -v. For behavioral changes, add a small isolated scenario and actual evidence or clearly label a decision-only assessment. Do not run against production data.

Report version, client/OS, relevant prompt, selected depths, observed result and sanitized evidence. Explain any changes to approval boundaries, GREEN or evidence floors in CHANGELOG.md.
