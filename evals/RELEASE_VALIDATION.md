# Local release validation

2026-09-08. Windows / Python 3.12. CI workflow not executed. These are package and demo checks, not a proof that every future model task is correct.

## .
Command: python -X utf8 tools/validate.py
Exit: 0

```text
PASS: structure, references, portability and release files

```

## .
Command: python -X utf8 -B -m unittest discover -s tests -v
Exit: 0

```text
test_install_refuses_overwrite_and_preserves_unrelated (test_manage.ManagementTests.test_install_refuses_overwrite_and_preserves_unrelated) ... ok
test_invalid_source_does_not_touch_existing_install (test_manage.ManagementTests.test_invalid_source_does_not_touch_existing_install) ... ok
test_uninstall_archives_and_retains_others (test_manage.ManagementTests.test_uninstall_archives_and_retains_others) ... ok
test_update_preserves_prior_files_outside_discovery_root (test_manage.ManagementTests.test_update_preserves_prior_files_outside_discovery_root) ... ok
test_update_rejects_unrelated_target (test_manage.ManagementTests.test_update_rejects_unrelated_target) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.274s

OK

```

## examples/business
Command: python -X utf8 -B -m unittest discover -v
Exit: 0

```text
test_empty (test_app.Tests.test_empty) ... ok
test_blank_strings_rejected_without_changing_rows (test_create.CreateTests.test_blank_strings_rejected_without_changing_rows) ... ok
test_non_strings_rejected_without_changing_rows (test_create.CreateTests.test_non_strings_rejected_without_changing_rows) ... ok
test_preserves_text_returns_id_and_commits_for_new_instance (test_create.CreateTests.test_preserves_text_returns_id_and_commits_for_new_instance) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.139s

OK

```

## examples/permission
Command: python -X utf8 -B -m unittest discover -v
Exit: 0

```text
test_allowed (test_access.Tests.test_allowed) ... ok
test_anonymous (test_access.Tests.test_anonymous) ... ok
test_anonymous_denied_for_each_tenant (test_access_regression.PermissionRegressionTests.test_anonymous_denied_for_each_tenant) ... ok
test_policy_truth_table_and_tenant_substitution (test_access_regression.PermissionRegressionTests.test_policy_truth_table_and_tenant_substitution) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK

```

Final audit: PASS — repository links, personal account-path scan, identical installed/exported skill, and only one active skill entry. Logs are sanitized copies.
