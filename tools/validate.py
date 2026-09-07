"""Structural package checks only; not a GREEN evaluator."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "slice-to-green"

def validate(root=ROOT):
    root = Path(root)
    skill = root / "skills" / "slice-to-green"
    errors = []
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append("Missing YAML frontmatter")
    header = text.split("---", 2)[1]
    for key in ("name: slice-to-green", "license: MIT", 'version: "0.1.0-alpha.1"'):
        if key not in header: errors.append("Missing metadata: " + key)
    if len(text.splitlines()) > 150: errors.append("Control plane exceeds 150 lines")
    main_links = set(re.findall(r"\]\((references/[^)#]+)", text))
    for ref in (skill / "references").glob("*.md"):
        if ref.relative_to(skill).as_posix() not in main_links:
            errors.append("Reference not discoverable from SKILL.md: " + ref.name)
    for p in skill.rglob("*"):
        if p.is_symlink(): errors.append("Symlink in distribution: " + str(p))
        if p.is_file() and p.suffix in (".md", ".yaml", ".svg"):
            body = p.read_text(encoding="utf-8")
            if re.search(r"[A-Za-z]:[\\/]Users[\\/]|/Users/|/home/[^/]+/", body):
                errors.append("Personal absolute path: " + str(p))
            for target in re.findall(r"\]\(([^)]+)\)", body):
                if "://" in target or target.startswith("#"): continue
                resolved = (p.parent / target.split("#")[0]).resolve()
                if not resolved.is_relative_to(skill.resolve()):
                    errors.append("Non-self-contained reference: " + target)
                elif not resolved.exists(): errors.append("Broken link: " + target)
    for file in ("README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md", "PROVENANCE.md"):
        if not (root / file).is_file(): errors.append("Missing release file: " + file)
    if (skill / "LICENSE").read_bytes() != (root / "LICENSE").read_bytes():
        errors.append("Skill/repository licenses differ")
    ET.parse(skill / "assets" / "icon.svg")
    return errors

if __name__ == "__main__":
    errors = validate()
    for error in errors: print("FAIL:", error)
    print("PASS: structure, references, portability and release files" if not errors else "NOT VALID")
    raise SystemExit(bool(errors))
