import unittest
from access import can_read


class PermissionRegressionTests(unittest.TestCase):
    def test_policy_truth_table_and_tenant_substitution(self):
        for record_tenant in ('a', 'b'):
            for actor_tenant in ('a', 'b'):
                for role in ('reader', 'writer', 'admin', ''):
                    with self.subTest(record_tenant=record_tenant,
                                      actor_tenant=actor_tenant, role=role):
                        expected = actor_tenant == record_tenant and role == 'reader'
                        self.assertIs(can_read(
                            {'tenant': actor_tenant, 'role': role},
                            {'tenant': record_tenant}), expected)

    def test_anonymous_denied_for_each_tenant(self):
        for tenant in ('a', 'b'):
            with self.subTest(tenant=tenant):
                self.assertIs(can_read(None, {'tenant': tenant}), False)


if __name__ == '__main__':
    unittest.main()
