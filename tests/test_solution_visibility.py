"""Static documentation regression only; these tests do not run or grade an AI."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/ts-code'


class SolutionVisibilityRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        cls.proposal = (SKILL / 'references/proposal.md').read_text(encoding='utf-8')
        cls.scope = cls.core.split('## 1.', 1)[1].split('## 2.', 1)[0]

    def test_brief_is_in_core_before_any_reference_is_needed(self):
        for required in ('首次实质修改', '代码/配置/数据/项目文件', '在对话',
                         '问题/结果', '做法与依据', '影响边界', '验证'):
            with self.subTest(required=required):
                self.assertIn(required, self.scope)
        self.assertIn('不要为小修复全量加载方案参考', self.proposal)

    def test_visibility_does_not_replace_permission(self):
        self.assertIn('方案可见 ≠ 需要确认', self.scope)
        self.assertIn('展示不改变授权边界', self.scope)
        self.assertIn('已批准或明确要求直接实施', self.scope)
        self.assertIn('新业务仍遵循一次确认', self.proposal)
        self.assertIn('不以“简单”自动豁免', self.proposal)

    def test_brief_does_not_add_documents_or_repeated_gates(self):
        for required in ('不另建文档', '机械修改可一句话', '已批准续做', '不逐工具播报'):
            with self.subTest(required=required):
                self.assertIn(required, self.scope)
        self.assertIn('不新增 Solution Brief 文件、状态字段或审批阶段', self.proposal)

    def test_unknown_causes_and_test_first_are_not_exempt(self):
        self.assertIn('原因未明列待查事实', self.scope)
        self.assertIn('确认后给修复摘要', self.scope)
        self.assertIn('先写复现测试或做隔离试验', self.proposal)
        self.assertIn('不必假装已经知道最终修法', self.proposal)
        self.assertIn('首轮最多 3 个诊断问题', self.core)

    def test_seven_design_content_areas_are_retained(self):
        numbers = re.findall(r'^(\d+)\. \*\*', self.proposal, re.M)
        self.assertEqual(numbers, ['1', '2', '3', '4', '5', '6', '7'])
        self.assertIn('只重新确认受影响部分', self.proposal)

    def test_replans_and_handoffs_are_visible(self):
        self.assertIn('方案/边界', self.scope)
        self.assertIn('在执行变更前', self.proposal)
        self.assertIn('交付对照摘要', self.scope)
        self.assertIn('超出批准范围先取得相应授权', self.proposal)

    def test_readonly_and_explicit_format_requests_are_preserved(self):
        self.assertIn('只设计/审查不改产品，只验证不修复', self.scope)
        self.assertIn('纯问答不插入方案卡', self.proposal)
        self.assertIn('用户明确限制输出形式', self.proposal)
        self.assertIn('不能跳过必要授权', self.proposal)

    def test_behavior_catalog_is_trace_based_and_not_a_claimed_run(self):
        value = json.loads((ROOT / 'evals/solution-visibility-scenarios.json').read_text(encoding='utf-8'))
        self.assertEqual(value['schema_version'], 1)
        self.assertEqual(value['kind'], 'MODEL_BEHAVIOR_SCENARIOS_NOT_RUN')
        self.assertIn('用户可见消息', value['review_protocol'])
        self.assertIn('首次实质修改', value['review_protocol'])
        cases = value['cases']
        self.assertEqual(len(cases), 10)
        self.assertEqual(len({case['id'] for case in cases}), len(cases))
        for case in cases:
            with self.subTest(case=case['id']):
                self.assertEqual(case['status'], 'NOT_RUN')
                self.assertTrue(case['prompt'] and case['expected'] and case['reject'])


if __name__ == '__main__':
    unittest.main()
