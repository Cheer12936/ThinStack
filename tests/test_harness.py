"""Test the evaluation machinery, not the capabilities of an AI model."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / 'evals/harness'
sys.path.insert(0, str(HARNESS))
spec = importlib.util.spec_from_file_location('ts_eval_run', HARNESS/'run.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
sys.path.pop(0)


class HarnessTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.work = self.root/'workspace'
        self.work.mkdir()

    def test_six_cases_have_unique_ids(self):
        self.assertEqual(len(h.CASES), 6)
        self.assertEqual(len({c['id'] for c in h.CASES}), 6)

    def test_noop_completion_is_rejected(self):
        c = h.CASES[0]
        for name, text in c['files'].items():
            h.write(self.work/name, text)
        before = h.hashes(self.work)
        result = h.grade(c, self.work, {'status':'complete'}, [], before, before, self.root)
        self.assertFalse(result['mechanical_acceptance_pass'])
        self.assertTrue(result['unsupported_completion'])

    def test_reference_solution_passes_independent_checks(self):
        c = h.CASES[0]
        for name, text in c['files'].items():
            h.write(self.work/name, text)
        before = h.hashes(self.work)
        h.write(self.work/c['module'], c['solution'])
        result = h.grade(c, self.work, {'status':'complete'}, [], before, h.hashes(self.work), self.root)
        self.assertTrue(result['mechanical_acceptance_pass'])
        self.assertTrue((self.root/'grader-result.json').exists())

    def test_unrelated_change_rejected(self):
        c = h.CASES[0]
        for name, text in c['files'].items():
            h.write(self.work/name, text)
        before = h.hashes(self.work)
        h.write(self.work/c['module'], c['solution'])
        h.write(self.work/'NOTES.md', 'unrelated change')
        result = h.grade(c, self.work, {'status':'complete'}, [], before, h.hashes(self.work), self.root)
        self.assertEqual(result['out_of_scope_paths'], ['NOTES.md'])
        self.assertFalse(result['mechanical_acceptance_pass'])

    def test_honest_blocked_external_case(self):
        c = h.CASES[-1]
        response = {'status':'blocked','message':'缺少真实凭据，不可认证'}
        result = h.grade(c, self.work, response, [response], {}, {}, self.root)
        self.assertTrue(result['mechanical_acceptance_pass'])
        self.assertTrue(result['semantic_review_required'])
        self.assertFalse(result['needless_blocking'])

    def test_clarification_requires_both_topics_and_review(self):
        c = h.CASES[1]
        history = [{'questions':[{'topic':'business_goal','text':'目标？'}]}, {'questions':[{'topic':'ownership','text':'归属？'}]}]
        result = h.grade(c, self.work, {'status':'complete'}, history, {}, {}, self.root)
        self.assertTrue(result['mechanical_acceptance_pass'])
        self.assertEqual(result['semantic_review'], 'NOT_REVIEWED')
        result = h.grade(c, self.work, {'status':'complete'}, history[:1], {}, {}, self.root)
        self.assertFalse(result['mechanical_acceptance_pass'])

    def test_protocol_rejects_empty_question(self):
        p = self.root/'reply.json'
        p.write_text(json.dumps({'status':'question','message':'','questions':[]}))
        with self.assertRaises(ValueError):
            h.parse_response(p)

    def test_output_never_overwritten(self):
        out = self.root/'results'
        out.mkdir()
        (out/'keep').write_text('original')
        with self.assertRaises(ValueError):
            h.execute(out, {'kind':'model','argv':[]})
        self.assertEqual((out/'keep').read_text(), 'original')

    def test_no_implicit_model_call(self):
        with self.assertRaises(SystemExit):
            h.main(['run','--output',str(self.root/'out')])

    def test_timed_out_process_is_a_failure(self):
        r = h.invoke([sys.executable,'-I','-c','import time; time.sleep(10)'], self.work, 0.1)
        self.assertTrue(r['timed_out'])
        self.assertNotEqual(r['exit_code'], 0)

    def test_all_arms_start_from_identical_sources(self):
        c = h.CASES[-1]
        adapter = {'kind':'deterministic-control','argv':[sys.executable,str(HARNESS/'control_adapter.py'),'{request}','{response}']}
        starts = []
        for arm in h.ARMS:
            result = h.run_trial(c, arm, 0, self.root/arm, adapter, 15)
            starts.append(result['start_snapshot_sha256'])
            self.assertIsNone(result['usage_reported'])
            self.assertIsNone(result['tool_call_count'])
            self.assertEqual(result['adapter_kind'], 'deterministic-control')
        self.assertEqual(len(set(starts)), 1)


if __name__ == '__main__':
    unittest.main()
