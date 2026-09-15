"""Validate emitted package metadata, links, budgets and runtime checksums; not agent behavior."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = Path("skills/ts-code")
MAX_CORE_BYTES = 10000


def runtime_hashes(root):
    root = Path(root)
    files = sorted((root / SKILL_PATH).rglob("*"))
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files if p.is_file() and not p.is_symlink()
            and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def validate(root=ROOT):
    root = Path(root).resolve()
    skill = root / SKILL_PATH
    errors = []
    try:
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        host = (skill / "agents/openai.yaml").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return ["Missing/unreadable entry metadata: " + str(exc)]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append("VERSION must use x.y.z")
    # This validates our deliberately small emitted YAML subset, not arbitrary YAML.
    parts = text.split("---\n", 2)
    if len(parts) != 3 or parts[0]:
        errors.append("Missing or malformed frontmatter")
        header = ""
    else:
        header = parts[1]
    for required in ("name: ts-code", "license: MIT", f'  version: "{version}"'):
        if required not in header.splitlines():
            errors.append("Metadata mismatch: " + required)
    descriptions = re.findall(r"^description: (.+)$", header, flags=re.M)
    if len(descriptions) != 1 or not 1 <= len(descriptions[0]) <= 1024:
        errors.append("description must be a single nonempty line, at most 1024 characters")
    if len(text.encode("utf-8")) > MAX_CORE_BYTES:
        errors.append("Core exceeds UTF-8 byte budget (not a token count)")
    if not re.search(r"^policy:\n  allow_implicit_invocation: false\s*$", host, re.M):
        errors.append("Explicit invocation policy missing")
    if "$ts-code" not in host:
        errors.append("Host default prompt must name $ts-code")
    if skill.is_symlink():
        errors.append("Symlink skill root")
    for path in skill.rglob("*"):
        if path.is_symlink():
            errors.append("Symlink in package: " + path.name)
            continue
        if not path.is_file() or path.suffix not in (".md", ".yaml"):
            continue
        try:
            body = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(str(exc))
            continue
        for target in re.findall(r"\]\(([^)]+)\)", body):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (path.parent / target.split("#")[0]).resolve()
            if not resolved.is_relative_to(skill) or not resolved.is_file():
                errors.append("Invalid package reference: " + target)
    try:
        if (skill / "LICENSE").read_bytes() != (root / "LICENSE").read_bytes():
            errors.append("License mismatch")
        ET.parse(skill / "assets/icon.svg")
        expected = json.loads((root / "SHA256SUMS.json").read_text(encoding="utf-8"))
        if expected != runtime_hashes(root):
            errors.append("Runtime checksum manifest is stale or has missing/extra entries")
    except (OSError, ValueError, ET.ParseError) as exc:
        errors.append("Invalid release asset/manifest: " + str(exc))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-checksums", action="store_true", help="Explicitly regenerate runtime-only manifest before validation")
    args = parser.parse_args()
    if args.write_checksums:
        (ROOT / "SHA256SUMS.json").write_text(json.dumps(runtime_hashes(ROOT), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    errors = validate()
    for error in errors:
        print("FAIL:", error)
    print("PACKAGE_VALID: structural/integrity checks only" if not errors else "PACKAGE_INVALID")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
