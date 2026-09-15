"""Validate a delivery record and local hashes; never run commands or certify truth."""
import argparse
import hashlib
import json
from pathlib import Path
import re

HEX = re.compile(r"[0-9a-f]{64}\Z")


def local_file(root, name):
    """Reject absolute paths, traversal and symlink escapes, including parent links."""
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        raise ValueError("Expected a portable relative path")
    path = Path(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("Path must remain inside the project root")
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Symlink evidence is not accepted")
    resolved = current.resolve()
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError("Evidence file is missing or outside root")
    return resolved


def check_record(record, root):
    """Return structural/integrity errors, not a judgment of test sufficiency."""
    root = Path(root).resolve()
    errors = []
    if not isinstance(record, dict):
        return ["Record must be an object"]
    if type(record.get("schema_version")) is not int or record["schema_version"] != 1:
        errors.append("schema_version must be 1")
    if not isinstance(record.get("scope"), str) or not record["scope"].strip():
        errors.append("scope must be nonempty")
    verdict = record.get("verdict")
    if verdict not in ("GREEN", "NOT_GREEN"):
        errors.append("verdict must be GREEN or NOT_GREEN")
    required = record.get("required")
    if not isinstance(required, list) or any(not isinstance(x, str) or not x.strip() for x in required):
        errors.append("required must be an array of nonempty criterion IDs")
        required = []
    elif len(set(required)) != len(required):
        errors.append("required IDs must be unique")
    snapshot = record.get("snapshot")
    if not isinstance(snapshot, dict):
        errors.append("snapshot must map source paths to SHA256 hashes")
        snapshot = {}
    checks = record.get("checks")
    if not isinstance(checks, list):
        errors.append("checks must be an array")
        checks = []
    risks = record.get("unresolved_high_risks")
    if not isinstance(risks, list) or any(not isinstance(x, str) or not x.strip() for x in risks):
        errors.append("unresolved_high_risks must be an array of nonempty descriptions")
        risks = ["invalid risk record"]

    def verify_hash(name, expected, label):
        try:
            if not isinstance(expected, str) or not HEX.fullmatch(expected):
                raise ValueError("Invalid SHA256")
            data = local_file(root, name).read_bytes()
            if label == "artifact" and not data:
                raise ValueError("Empty evidence artifact")
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError("Hash mismatch; evidence or source changed")
        except (ValueError, OSError) as exc:
            errors.append(f"{label} {name!r}: {exc}")

    for name, digest in snapshot.items():
        verify_hash(name, digest, "source")
    covered = set()
    for i, check in enumerate(checks):
        if not isinstance(check, dict):
            errors.append(f"check {i}: expected object")
            continue
        status = check.get("status")
        if status not in ("pass", "fail", "skipped"):
            errors.append(f"check {i}: invalid status")
        covers = check.get("covers")
        if not isinstance(covers, list) or not covers or any(not isinstance(x, str) or x not in required for x in covers):
            errors.append(f"check {i}: covers must reference required IDs")
            covers = []
        for field in ("method", "observed_at", "environment"):
            if not isinstance(check.get(field), str) or not check[field].strip():
                errors.append(f"check {i}: missing {field}")
        if status in ("pass", "fail"):
            verify_hash(check.get("artifact"), check.get("sha256"), "artifact")
        if status == "pass":
            covered.update(covers)
        if verdict == "GREEN" and status != "pass":
            errors.append(f"check {i}: GREEN cannot contain failed or skipped required checks")
    if verdict == "GREEN":
        if not required or not snapshot or not checks:
            errors.append("GREEN needs criteria, a source snapshot and checks")
        if set(required) - covered:
            errors.append("GREEN has uncovered criteria: " + ", ".join(sorted(set(required) - covered)))
        if risks:
            errors.append("GREEN has unresolved high risks")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--root", required=True, type=Path, help="Explicit project root; no network or commands executed")
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
        errors = check_record(record, args.root)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"RECORD_ERROR: {exc}\n")
    for error in errors:
        print("FAIL:", error)
    print("RECORD_INVALID" if errors else "RECORD_VALID: integrity only; not proof of correctness or genuine execution")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
