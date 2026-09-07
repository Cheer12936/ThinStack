import importlib.util
from pathlib import Path
import tempfile
import unittest

path = Path(__file__).resolve().parents[1] / "tools" / "manage.py"
spec = importlib.util.spec_from_file_location("manage", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ManagementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "skills"
        self.source = Path(self.tmp.name) / "source"
        self.source.mkdir()
        (self.source / "SKILL.md").write_text("---\nname: slice-to-green\n---\n", encoding="utf-8")
        (self.source / "content.txt").write_text("v1", encoding="utf-8")

    def test_install_refuses_overwrite_and_preserves_unrelated(self):
        target = module.manage("install", self.root, self.source)
        (self.root / "unrelated.txt").write_text("keep")
        with self.assertRaises(ValueError):
            module.manage("install", self.root, self.source)
        self.assertEqual((target / "content.txt").read_text(), "v1")
        self.assertEqual((self.root / "unrelated.txt").read_text(), "keep")

    def test_update_preserves_prior_files_outside_discovery_root(self):
        target = module.manage("install", self.root, self.source)
        (target / "user-note.txt").write_text("custom")
        (self.source / "content.txt").write_text("v2")
        backup = module.manage("update", self.root, self.source)
        self.assertEqual((backup / "user-note.txt").read_text(), "custom")
        self.assertEqual((backup / "content.txt").read_text(), "v1")
        self.assertEqual((target / "content.txt").read_text(), "v2")
        self.assertFalse(backup.is_relative_to(self.root))

    def test_uninstall_archives_and_retains_others(self):
        target = module.manage("install", self.root, self.source)
        (self.root / "other").mkdir()
        backup = module.manage("uninstall", self.root)
        self.assertFalse(target.exists())
        self.assertTrue((backup / "SKILL.md").exists())
        self.assertTrue((self.root / "other").is_dir())

    def test_update_rejects_unrelated_target(self):
        self.root.mkdir()
        target = self.root / "slice-to-green"
        target.mkdir()
        (target / "SKILL.md").write_text("---\nname: unrelated\n---\n")
        with self.assertRaises(ValueError):
            module.manage("update", self.root, self.source)
        self.assertIn("unrelated", (target / "SKILL.md").read_text())

    def test_invalid_source_does_not_touch_existing_install(self):
        target = module.manage("install", self.root, self.source)
        (self.source / "SKILL.md").write_text("---\nname: invalid\n---\n")
        with self.assertRaises(ValueError):
            module.manage("update", self.root, self.source)
        self.assertEqual((target / "content.txt").read_text(), "v1")

if __name__ == "__main__": unittest.main()
