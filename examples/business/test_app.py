import tempfile, unittest
from pathlib import Path
from app import Notes

class Tests(unittest.TestCase):
    def test_empty(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(Notes(Path(d)/"notes.db").list(), [])

if __name__ == "__main__": unittest.main()
