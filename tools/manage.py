"""Install/archive only the explicitly targeted ts-code skill; stdlib only."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import os
import re
import shutil
import tempfile
import uuid

NAME = "ts-code"
SOURCE = Path(__file__).resolve().parents[1] / "skills" / NAME

def check_skill(path):
    if path.is_symlink() or not path.is_dir():
        raise ValueError("Expected an ordinary skill directory")
    for item in path.rglob("*"):
        if item.is_symlink():
            raise ValueError("Symlinks inside a skill are not supported")
    content = (path / "SKILL.md").read_text(encoding="utf-8")
    if "name: ts-code" not in content.split("---")[1]:
        raise ValueError("Target is not a ts-code skill")

def invocation_enabled(path):
    manifest = path / "agents" / "openai.yaml"
    text = manifest.read_text(encoding="utf-8")
    matches = re.findall(r"^(\s*allow_implicit_invocation:\s*)(true|false)\s*$", text, re.M)
    if len(matches) != 1:
        raise ValueError("Expected one allow_implicit_invocation policy")
    return matches[0][1] == "true"

def set_invocation(path, enabled):
    manifest = path / "agents" / "openai.yaml"
    text = manifest.read_text(encoding="utf-8")
    updated, count = re.subn(r"^(\s*allow_implicit_invocation:\s*)(?:true|false)\s*$",
                             lambda match: match.group(1) + ("true" if enabled else "false"),
                             text, flags=re.M)
    if count != 1:
        raise ValueError("Expected one allow_implicit_invocation policy")
    manifest.write_text(updated, encoding="utf-8")

def manage(action, skills_dir, source=SOURCE, invocation=None, project_root=None):
    root = Path(skills_dir).expanduser().resolve()
    if invocation not in (None, "explicit", "project", "preserve"):
        raise ValueError("Invalid invocation profile")
    if action == "uninstall" and (invocation is not None or project_root is not None):
        raise ValueError("Invocation options do not apply to uninstall")
    if action == "install" and invocation == "preserve":
        raise ValueError("Install cannot preserve a policy that does not exist")
    profile = invocation or ("preserve" if action == "update" else "explicit")
    if profile == "project":
        if project_root is None:
            raise ValueError("Project invocation requires --project-root")
        project = Path(project_root).expanduser().resolve()
        expected = project / ".agents" / "skills"
        if not project.is_dir() or root != expected:
            raise ValueError("Project invocation requires PROJECT_ROOT/.agents/skills")
    elif project_root is not None:
        raise ValueError("--project-root requires --invocation project")
    if action == "install":
        root.mkdir(parents=True, exist_ok=True)
    if not root.is_dir():
        raise ValueError("Skills directory does not exist")
    target = root / NAME
    if target.is_symlink():
        raise ValueError("Refusing a symlink target")
    if target.resolve().parent != root:
        raise ValueError("Target escaped the explicit skills directory")
    if action == "install" and target.exists():
        raise ValueError("Already installed; use update to preserve a backup")
    if action in ("update", "uninstall"):
        check_skill(target)
    if action != "uninstall":
        check_skill(Path(source))
    preserved_invocation = invocation_enabled(target) if action == "update" and profile == "preserve" else None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = root.parent / (root.name + "-ts-code-backups")
    if backup_root.is_symlink():
        raise ValueError("Refusing a symlink backup directory")
    backup = backup_root / (stamp + "-" + uuid.uuid4().hex[:8])
    if action == "uninstall":
        backup_root.mkdir(exist_ok=True)
        target.rename(backup)
        return backup
    stage = Path(tempfile.mkdtemp(prefix=".ts-code-stage-", dir=root))
    # The generated, checked staging directory contains only the copied package.
    try:
        shutil.copytree(source, stage, dirs_exist_ok=True)
        if profile == "project":
            set_invocation(stage, True)
        elif profile == "explicit":
            set_invocation(stage, False)
        elif profile == "preserve":
            set_invocation(stage, preserved_invocation)
        check_skill(stage)
        if action == "update":
            backup_root.mkdir(exist_ok=True)
            target.rename(backup)
        try:
            stage.rename(target)
        except Exception:
            if action == "update" and not target.exists():
                backup.rename(target)
            raise
    finally:
        if stage.exists():
            if stage.resolve().parent != root or not stage.name.startswith(".ts-code-stage-"):
                raise ValueError("Unexpected staging cleanup target")
            shutil.rmtree(stage)
    return backup if action == "update" else target

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["install", "update", "uninstall"])
    parser.add_argument("--skills-dir", required=True, help="Explicit client skill-discovery directory")
    parser.add_argument("--invocation", choices=["explicit", "project", "preserve"],
                        help="Install defaults to explicit; update defaults to preserving the installed policy")
    parser.add_argument("--project-root", help="Required for project profile; skills directory must be PROJECT_ROOT/.agents/skills")
    args = parser.parse_args()
    try:
        result = manage(args.action, args.skills_dir, invocation=args.invocation,
                        project_root=args.project_root)
    except (ValueError, OSError, IndexError) as exc:
        parser.exit(1, str(exc) + "\n")
    print(("Installed: " if args.action == "install" else "Archived previous version: ") + str(result))

if __name__ == "__main__":
    main()
