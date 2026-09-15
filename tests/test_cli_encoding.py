"""The CLI must preserve its result under a Windows-style legacy pipe encoding."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from test_project_state import fixture, SCRIPT


class EncodingTests(unittest.TestCase):
    def test_json_output_uses_utf8_despite_legacy_pipe(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture(Path(directory))
            env = dict(os.environ, PYTHONIOENCODING='cp1252', PYTHONUTF8='0')
            result = subprocess.run([sys.executable, '-B', str(SCRIPT), 'doctor',
                                     '--root', directory, '--json'],
                                    capture_output=True, env=env, timeout=15)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads(result.stdout.decode('utf-8'))
            self.assertEqual(report['result'], 'PROJECT_INVALID')
            self.assertIn('结构', report['meaning'])


if __name__ == '__main__':
    unittest.main()
