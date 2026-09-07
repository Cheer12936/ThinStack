import tempfile
import unittest
from pathlib import Path

from app import Notes


class CreateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "notes.db"
        self.notes = Notes(self.path)

    def test_preserves_text_returns_id_and_commits_for_new_instance(self):
        texts = ["  原文\n", "x'); DROP TABLE notes; --", "重复", "重复"]
        ids = [self.notes.create(text) for text in texts]
        self.assertTrue(all(type(note_id) is int and note_id > 0 for note_id in ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(Notes(self.path).list(), sorted(zip(ids, texts)))

    def test_blank_strings_rejected_without_changing_rows(self):
        saved_id = self.notes.create("existing")
        for value in ["", " ", "\t\r\n", "\u3000\u00a0"]:
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    self.notes.create(value)
                self.assertEqual(Notes(self.path).list(), [(saved_id, "existing")])

    def test_non_strings_rejected_without_changing_rows(self):
        for value in [None, 0, 1, False, 1.2, b"text", [], {}, object()]:
            with self.subTest(value=repr(value)):
                with self.assertRaises(TypeError):
                    self.notes.create(value)
                self.assertEqual(Notes(self.path).list(), [])


if __name__ == "__main__":
    unittest.main()
