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
adapter_spec = importlib.util.spec_from_file_location('codex_cli_adapter', HARNESS/'codex_cli_adapter.py')
codex_adapter = importlib.util.module_from_spec(adapter_spec)
adapter_spec.loader.exec_module(codex_adapter)


class HarnessTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.work = self.root/'workspace'
        self.work.mkdir()

    def test_seven_cases_have_unique_ids(self):
        self.assertEqual(len(h.CASES), 7)
        self.assertEqual(len({c['id'] for c in h.CASES}), 7)

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
        c = next(case for case in h.CASES if case['id'] == 'clarify')
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

    def test_coupon_migration_control_changes_only_local_database(self):
        c = next(case for case in h.CASES if case['id'] == 'coupon_migration')
        adapter = {'kind':'deterministic-control','argv':[sys.executable,str(HARNESS/'control_adapter.py'),'{request}','{response}']}
        result = h.run_trial(c, 'autonomous', 0, self.root/'migration', adapter, 15)
        self.assertTrue(result['grade']['mechanical_acceptance_pass'])
        self.assertEqual(result['grade']['changed_files'], ['local.db'])

    def test_custom_arm_config_uses_immutable_skill_roots(self):
        config = self.root/'arms.json'
        config.write_text(json.dumps({'schema_version':1, 'arms':[
            {'name':'bare','skill_root':None,'mode':'autonomous'},
            {'name':'candidate','skill_root':str(ROOT/'skills/ts-code'),'mode':'autonomous'}
        ]}), encoding='utf-8')
        arms = h.load_arms(config)
        self.assertEqual([arm['name'] for arm in arms], ['bare', 'candidate'])
        self.assertTrue(Path(arms[1]['skill_root']).is_absolute())

    def test_codex_adapter_uses_isolated_skill_discovery_and_real_usage_only(self):
        cmd = codex_adapter.command('model-id', 'medium', self.root/'last.json', HARNESS/'response-schema.json')
        self.assertIn('skip_host_skill_discovery', cmd)
        self.assertIn('--ignore-user-config', cmd)
        self.assertIn('--approve-for-me', cmd)
        self.assertNotIn('--sandbox', cmd)
        self.assertEqual(codex_adapter.usage_from_events('{"usage":{"input_tokens":12}}\n'), {'input_tokens': 12})
        self.assertIsNone(codex_adapter.usage_from_events('not-json\n'))


if __name__ == '__main__':
    unittest.main()
