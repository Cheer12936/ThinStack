"""Package and evidence-validator regression tests, not a model benchmark."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load("package_validator", ROOT / "tools/validate.py")
evidence = load("evidence_validator", ROOT / "skills/ts-code/scripts/check_evidence.py")
manager = load("package_manager", ROOT / "tools/manage.py")


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "app.py").write_text("result = 1\n", encoding="utf-8")
        (self.root / "test.log").write_text("PASS AC-1\n", encoding="utf-8")
        digest = lambda p: hashlib.sha256((self.root / p).read_bytes()).hexdigest()
        self.record = {"schema_version": 1, "scope": "Slice 1", "verdict": "GREEN",
                       "required": ["AC-1"], "snapshot": {"app.py": digest("app.py")},
                       "unresolved_high_risks": [], "checks": [{"covers": ["AC-1"], "status": "pass",
                       "method": "python -m unittest", "observed_at": "2026-09-15T00:00:00Z",
                       "environment": "isolated test fixture", "artifact": "test.log", "sha256": digest("test.log")}]}

    def errors(self):
        return evidence.check_record(self.record, self.root)

    def test_valid_record(self):
        self.assertEqual(self.errors(), [])

    def test_source_change_invalidates_record(self):
        (self.root / "app.py").write_text("result = 2\n")
        self.assertTrue(self.errors())

    def test_artifact_change_invalidates_record(self):
        (self.root / "test.log").write_text("edited")
        self.assertTrue(self.errors())

    def test_missing_artifact(self):
        (self.root / "test.log").unlink()
        self.assertTrue(self.errors())

    def test_uncovered_acceptance(self):
        self.record["required"].append("AC-2")
        self.assertTrue(self.errors())

    def test_failed_check(self):
        self.record["checks"][0]["status"] = "fail"
        self.assertTrue(self.errors())

    def test_skipped_check(self):
        self.record["checks"][0]["status"] = "skipped"
        self.assertTrue(self.errors())

    def test_unknown_criterion(self):
        self.record["checks"][0]["covers"] = ["unknown"]
        self.assertTrue(self.errors())

    def test_unresolved_high_risk(self):
        self.record["unresolved_high_risks"] = ["authorization not proven"]
        self.assertTrue(self.errors())

    def test_no_empty_green(self):
        self.record["required"], self.record["checks"], self.record["snapshot"] = [], [], {}
        self.assertTrue(self.errors())

    def test_path_traversal_rejected(self):
        for path in ("../test.log", "/tmp/test.log", "C:\\test.log"):
            with self.subTest(path=path):
                self.record["checks"][0]["artifact"] = path
                self.assertTrue(self.errors())

    def test_wrong_field_types(self):
        for field, value in (("schema_version", True), ("required", [None]), ("snapshot", []), ("checks", {}), ("unresolved_high_risks", None)):
            original = copy.deepcopy(self.record)
            self.record[field] = value
            with self.subTest(field=field):
                self.assertTrue(self.errors())
            self.record = original

    def test_blocked_record_is_not_green(self):
        self.record.update(verdict="NOT_GREEN", snapshot={}, checks=[], unresolved_high_risks=["missing credentials"])
        self.assertEqual(self.errors(), [])

    def test_cli_returns_nonzero_on_bad_record(self):
        path = self.root / "record.json"
        self.record["checks"][0]["status"] = "skipped"
        path.write_text(json.dumps(self.record), encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", str(ROOT / "skills/ts-code/scripts/check_evidence.py"), str(path), "--root", str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("RECORD_INVALID", result.stdout)

    def test_symlink_evidence_rejected(self):
        try:
            (self.root / "alias.log").symlink_to(self.root / "test.log")
        except OSError:
            self.skipTest("Symlinks not permitted in this environment")
        self.record["checks"][0]["artifact"] = "alias.log"
        self.assertTrue(self.errors())


class PackageTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        shutil.copytree(ROOT / "skills", self.root / "skills", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for name in ("VERSION", "LICENSE", "SHA256SUMS.json"):
            shutil.copy2(ROOT / name, self.root / name)

    def test_current_package(self):
        self.assertEqual(validator.validate(self.root), [])

    def test_version_mismatch(self):
        (self.root / "VERSION").write_text("0.3.0\n")
        self.assertTrue(validator.validate(self.root))

    def test_checksum_tampering(self):
        (self.root / "skills/ts-code/references/tdd.md").write_text("tampered")
        self.assertTrue(validator.validate(self.root))

    def test_extra_runtime_file(self):
        (self.root / "skills/ts-code/references/old-policy.md").write_text("old")
        self.assertTrue(validator.validate(self.root))

    def test_missing_runtime_file(self):
        (self.root / "skills/ts-code/references/tdd.md").unlink()
        self.assertTrue(validator.validate(self.root))

    def test_broken_link(self):
        path = self.root / "skills/ts-code/SKILL.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[bad](references/missing.md)\n", encoding="utf-8")
        self.assertTrue(any("reference" in e for e in validator.validate(self.root)))

    def test_malformed_frontmatter(self):
        (self.root / "skills/ts-code/SKILL.md").write_text("# no metadata")
        self.assertTrue(validator.validate(self.root))

    def test_actual_v020_install_update_uninstall(self):
        discovery = self.root / "client-skills"
        source = self.root / "skills/ts-code"
        target = manager.manage("install", discovery, source)
        (target / "local-note.md").write_text("keep")
        (target / "references/old-policy.md").write_text("legacy")
        backup = manager.manage("update", discovery, source)
        self.assertEqual((backup / "local-note.md").read_text(), "keep")
        self.assertTrue((backup / "references/old-policy.md").exists())
        self.assertFalse((target / "references/old-policy.md").exists())
        self.assertTrue((target / "scripts/check_evidence.py").exists())
        final_backup = manager.manage("uninstall", discovery)
        self.assertTrue((final_backup / "SKILL.md").exists())
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
