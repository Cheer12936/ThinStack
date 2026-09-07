"""Install/archive only the explicitly targeted thinslack-code skill; stdlib only."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import os
import shutil
import tempfile
import uuid

NAME = "thinslack-code"
SOURCE = Path(__file__).resolve().parents[1] / "skills" / NAME

def check_skill(path):
    if path.is_symlink() or not path.is_dir():
        raise ValueError("Expected an ordinary skill directory")
    for item in path.rglob("*"):
        if item.is_symlink():
            raise ValueError("Symlinks inside a skill are not supported")
    content = (path / "SKILL.md").read_text(encoding="utf-8")
    if "name: thinslack-code" not in content.split("---")[1]:
        raise ValueError("Target is not a thinslack-code skill")

def manage(action, skills_dir, source=SOURCE):
    root = Path(skills_dir).expanduser().resolve()
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
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = root.parent / (root.name + "-thinslack-code-backups")
    if backup_root.is_symlink():
        raise ValueError("Refusing a symlink backup directory")
    backup = backup_root / (stamp + "-" + uuid.uuid4().hex[:8])
    if action == "uninstall":
        backup_root.mkdir(exist_ok=True)
        target.rename(backup)
        return backup
    stage = Path(tempfile.mkdtemp(prefix=".thinslack-code-stage-", dir=root))
    # The generated, checked staging directory contains only the copied package.
    try:
        shutil.copytree(source, stage, dirs_exist_ok=True)
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
            if stage.resolve().parent != root or not stage.name.startswith(".thinslack-code-stage-"):
                raise ValueError("Unexpected staging cleanup target")
            shutil.rmtree(stage)
    return backup if action == "update" else target

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["install", "update", "uninstall"])
    parser.add_argument("--skills-dir", required=True, help="Explicit client skill-discovery directory")
    args = parser.parse_args()
    try:
        result = manage(args.action, args.skills_dir)
    except (ValueError, OSError, IndexError) as exc:
        parser.exit(1, str(exc) + "\n")
    print(("Installed: " if args.action == "install" else "Archived previous version: ") + str(result))

if __name__ == "__main__":
    main()
