import unittest
from access import can_read

class Tests(unittest.TestCase):
    def test_allowed(self):
        self.assertTrue(can_read({"tenant":"a","role":"reader"}, {"tenant":"a"}))
    def test_anonymous(self):
        self.assertFalse(can_read(None, {"tenant":"a"}))

if __name__ == "__main__": unittest.main()
