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


class AgentCallBudgetTests(unittest.TestCase):
    """Deterministic protocol controls, not evidence that a model asks good questions."""
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.case = next(c for c in h.CASES if c['id'] == 'clarify')

    def adapter(self, batches=4, batch_size=1, terminal='complete'):
        script = self.root / 'scripted_adapter.py'
        script.write_text(
            "import json, sys\nfrom pathlib import Path\n"
            "r=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))\n"
            "n=len(r['history'])\n"
            f"questions=[{{'topic': ['business_goal','ownership'][i] if i<2 else 'other', 'text': 'Fixture question '+str(i)}} for i in range(n*{batch_size},(n+1)*{batch_size})] if n<{batches} else []\n"
            f"reply={{'status':'question' if questions else {terminal!r},'message':'DETERMINISTIC PROTOCOL CONTROL; missing credentials','questions':questions,'usage':None}}\n"
            "Path(sys.argv[2]).write_text(json.dumps(reply),encoding='utf-8')\n",
            encoding='utf-8')
        return {'kind': 'deterministic-control',
                'argv': [sys.executable, str(script), '{request}', '{response}']}

    def trial(self, *, budget=5, batches=4, batch_size=1):
        return h.run_trial(self.case, 'bare', 0, self.root/'trial',
                           self.adapter(batches, batch_size), 15,
                           max_agent_calls=budget)

    def test_four_question_batches_can_receive_a_fifth_delivery_call(self):
        r = self.trial(budget=5)
        self.assertEqual(r['adapter_invocations'], 5)
        self.assertEqual(r['question_batches'], 4)
        self.assertEqual(r['stop_reason'], 'complete')
        self.assertTrue(r['grade']['mechanical_acceptance_pass'])
        self.assertEqual(r['grade']['semantic_review'], 'NOT_REVIEWED')
        self.assertFalse(r['budget_exhausted'])
        self.assertIsNone(r['usage_reported'])

    def test_budget_exhaustion_is_incomplete_not_fabricated_completion(self):
        r = self.trial(budget=4)
        self.assertEqual(r['adapter_invocations'], 4)
        self.assertEqual(r['stop_reason'], 'agent_call_budget_exhausted')
        self.assertTrue(r['budget_exhausted'])
        self.assertEqual(r['status'], 'question')
        self.assertIsNone(r['protocol_error'])
        self.assertFalse(r['grade']['mechanical_acceptance_pass'])
        self.assertFalse(r['grade']['unsupported_completion'])
        self.assertFalse(r['grade']['needless_blocking'])
        self.assertFalse((self.root/'trial/request-4.json').exists())
        trace = json.loads((self.root/'trial/interaction.json').read_text())
        self.assertEqual(len(trace['history']), 4)
        self.assertEqual(len(trace['answers']), 4)
        self.assertEqual(trace['answers'][-1]['question'], 'Fixture question 3')

    def test_default_budget_retains_previous_call_limit(self):
        r = h.run_trial(self.case, 'bare', 0, self.root/'trial', self.adapter(), 15)
        self.assertEqual(r['max_agent_calls'], 4)
        self.assertEqual(r['adapter_invocations'], 4)
        self.assertTrue(r['budget_exhausted'])

    def test_completion_on_last_allowed_call_is_not_budget_exhaustion(self):
        r = self.trial(budget=3, batches=2)
        self.assertEqual(r['adapter_invocations'], 3)
        self.assertEqual(r['stop_reason'], 'complete')
        self.assertFalse(r['budget_exhausted'])
        self.assertTrue(r['grade']['mechanical_acceptance_pass'])

    def test_batched_questions_are_not_multiple_agent_calls(self):
        r = self.trial(budget=2, batches=1, batch_size=3)
        self.assertEqual(r['adapter_invocations'], 2)
        self.assertEqual(r['question_batches'], 1)
        self.assertEqual(r['grade']['question_count'], 3)
        self.assertTrue(r['grade']['mechanical_acceptance_pass'])

    def test_more_budget_does_not_force_extra_calls_after_completion(self):
        r = self.trial(budget=10, batches=2)
        self.assertEqual(r['adapter_invocations'], 3)
        self.assertFalse((self.root/'trial/request-3.json').exists())

    def test_invalid_budget_rejected_before_any_workspace_writes(self):
        for value in (0, -1, 101, 1.5, True, '5', None):
            with self.subTest(value=value):
                directory = self.root/'trial'
                with self.assertRaises(ValueError):
                    h.run_trial(self.case, 'bare', 0, directory,
                                {'kind': 'deterministic-control', 'argv': []}, 15,
                                max_agent_calls=value)
                self.assertFalse(directory.exists())
                with self.assertRaises(ValueError):
                    h.execute(self.root/'out', {}, max_agent_calls=value)
                self.assertFalse((self.root/'out').exists())

    def test_cli_validates_budget_before_execution(self):
        for value in ('0', '-1', '101', '1.5'):
            with self.subTest(value=value), self.assertRaises(SystemExit) as cm:
                h.main(['selftest', '--output', str(self.root/'out'),
                        '--max-agent-calls', value])
            self.assertEqual(cm.exception.code, 2)
        self.assertFalse((self.root/'out').exists())

    def test_cli_passes_budget_to_both_control_groups(self):
        out = self.root/'selftest'
        code = h.main(['selftest', '--output', str(out), '--case', 'clarify',
                       '--max-agent-calls', '1'])
        self.assertEqual(code, 1)  # Too little budget; do not hide this failure.
        for label in ('positive', 'negative'):
            summary = json.loads((out/label/'summary.json').read_text())
            self.assertEqual(summary['max_agent_calls'], 1)
        pos = json.loads((out/'positive/summary.json').read_text())
        self.assertEqual(pos['stop_reason_counts']['agent_call_budget_exhausted'], 3)
        self.assertEqual(pos['unsupported_completion'], 0)

    def test_summary_records_same_budget_and_reasons_for_every_arm(self):
        arms = h.default_arms()[:2]
        summary = h.execute(self.root/'out', self.adapter(), cases=[self.case],
                            arms=arms, max_agent_calls=5)
        self.assertEqual(summary['max_agent_calls'], 5)
        self.assertEqual(summary['timeout_seconds_per_call'], 120)
        self.assertEqual(summary['stop_reason_counts'], {'complete': 2})
        self.assertEqual(summary['mechanical_pass'], 2)
        for result in summary['results']:
            self.assertEqual(result['max_agent_calls'], 5)
            self.assertEqual(result['adapter_invocations'], 5)
        for result in summary['by_arm'].values():
            self.assertEqual(result['stop_reason_counts'], {'complete': 1})

    def test_timeout_is_not_an_agent_reported_blocker_or_call_exhaustion(self):
        outcome = {'exit_code': -1, 'timed_out': True, 'seconds': 1,
                   'stdout': '', 'stderr': ''}
        with patch.object(h, 'invoke', return_value=outcome):
            r = h.run_trial(self.case, 'bare', 0, self.root/'trial',
                            {'kind':'deterministic-control','argv':['unused']}, 1)
        self.assertEqual(r['stop_reason'], 'adapter_timeout')
        self.assertFalse(r['budget_exhausted'])
        self.assertFalse(r['grade']['needless_blocking'])
        self.assertFalse(r['grade']['mechanical_acceptance_pass'])
        self.assertFalse(r['grade']['unsupported_completion'])

    def test_adapter_failure_and_invalid_response_are_separate_reasons(self):
        for bad_json in (False, True):
            with self.subTest(bad_json=bad_json):
                directory = self.root/str(bad_json)
                def fail(argv, cwd, timeout):
                    if bad_json:
                        (directory/'response-0.json').write_text('{broken')
                    return {'exit_code':0 if bad_json else 1, 'timed_out':False,
                            'seconds':0, 'stdout':'', 'stderr':''}
                with patch.object(h, 'invoke', side_effect=fail):
                    r = h.run_trial(self.case, 'bare', 0, directory,
                                    {'kind':'deterministic-control','argv':['unused']}, 15)
                self.assertEqual(r['stop_reason'], 'protocol_error' if bad_json else 'adapter_error')
                self.assertFalse(r['grade']['needless_blocking'])
                self.assertFalse(r['budget_exhausted'])

    def test_honest_external_blocking_remains_a_valid_result(self):
        r = h.run_trial(h.CASES[-1], 'bare', 0, self.root/'trial',
                        self.adapter(batches=0, terminal='blocked'), 15,
                        max_agent_calls=1)
        self.assertEqual(r['stop_reason'], 'blocked')
        self.assertFalse(r['budget_exhausted'])
        self.assertTrue(r['grade']['mechanical_acceptance_pass'])


class ClarificationPolicyTests(unittest.TestCase):
    """Static policy-presence checks only; no model behavior is certified."""
    def test_one_authoritative_runtime_source_and_distinct_stop_outcomes(self):
        body = (ROOT/'skills/ts-code/references/clarify.md').read_text(encoding='utf-8')
        for phrase in ('唯一运行规则来源', '一批提问及用户对这批问题的回答',
                       '不要求至少问两轮', '两轮不是访谈上限',
                       '已澄清', '暂时无法澄清', '仍阻止依赖实现'):
            self.assertIn(phrase, body)

    def test_readme_links_policy_without_repeating_numeric_grill_limits(self):
        body = (ROOT/'README.md').read_text(encoding='utf-8')
        self.assertIn('skills/ts-code/references/clarify.md', body)
        self.assertNotIn('初始化前两轮', body)
        self.assertNotIn('最多 3 个', body)

    def test_diagnostic_budget_is_not_removed_or_used_as_grill_limit(self):
        core = (ROOT/'skills/ts-code/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('首轮最多 3 个诊断问题', core)
        self.assertIn('不适用于 Grill', core)
        self.assertLessEqual(len(core.encode('utf-8')), 10000)


if __name__ == '__main__':
    unittest.main()
