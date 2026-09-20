"""Regression reproductions for v0.3.2 registration; no model or production calls."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/ts-code/scripts/project_state.py'
spec = importlib.util.spec_from_file_location('registration_under_test', SCRIPT)
ps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ps)


class RegistrationSafetyTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()

    def add(self, **kwargs):
        return ps.register_slice(self.root, title='Next', goal='A concrete outcome', module='test', **kwargs)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob('*') if p.is_file()}

    def edit(self, path, **changes):
        p = self.root / path
        text = p.read_text(encoding='utf-8')
        m = ps.BLOCK.search(text)
        record = json.loads(m.group(1))
        record.update(changes)
        p.write_text(text[:m.start(1)] + json.dumps(record, ensure_ascii=False, indent=2) + text[m.end(1):], encoding='utf-8')
        return record

    def test_clean_first_add_and_doctor(self):
        r = self.add()
        self.assertEqual(r['id'], 'S-001')
        self.assertEqual(r['path'], 'docs/slices/S-001.md')
        self.assertFalse(ps.Project(self.root).inspect().issues)

    def test_existing_record_bytes_preserved(self):
        r = self.add()
        before = (self.root/r['path']).read_bytes()
        r2 = self.add(dependencies=['S-001'])
        self.assertEqual(r2['id'], 'S-002')
        self.assertEqual((self.root/r['path']).read_bytes(), before)

    def test_no_baselines_pinned_to_future_records(self):
        self.add()
        self.add(scope='deferred')
        (self.root/'docs/architecture/BASELINE.md').write_text('# New confirmed rule', encoding='utf-8')
        p = ps.Project(self.root).inspect()
        self.assertTrue(all(row['record']['baseline_refs'] == {} for row in p.rows))
        self.assertFalse(any(i['code'] == 'baseline_changed' for i in p.issues))

    def test_explicit_binding_is_limited_to_selected_baselines(self):
        self.add()
        cfg_path = self.root/'.thinstack.json'
        cfg = json.loads(cfg_path.read_text(encoding='utf-8'))
        other = 'docs/other.md'
        (self.root/other).write_text('# Other rules', encoding='utf-8')
        cfg['baselines'].append(other)
        cfg_path.write_text(json.dumps(cfg), encoding='utf-8')
        r = self.add(baselines=[other])
        row = next(x['record'] for x in ps.Project(self.root).inspect().rows if x['record']['id'] == r['id'])
        self.assertEqual(row['baseline_refs'], {other: ps.digest((self.root/other).read_bytes())})
        (self.root/other).write_text('# Changed', encoding='utf-8')
        self.assertTrue(any(i['code'] == 'baseline_changed' for i in ps.Project(self.root).inspect().issues))

    def test_does_not_silently_clear_existing_pins(self):
        self.add()
        name = 'docs/architecture/BASELINE.md'
        r = self.add(baselines=[name])
        before = (self.root/r['path']).read_bytes()
        self.add()
        self.assertEqual(before, (self.root/r['path']).read_bytes())

    def test_missing_or_unregistered_baseline_rejected_without_writes(self):
        self.add()
        (self.root/'not_registered.md').write_text('rules')
        before = self.snapshot()
        with self.assertRaises(ValueError): self.add(baselines=['not_registered.md'])
        self.assertEqual(before, self.snapshot())

    def test_cannot_bind_unconfirmed_new_template(self):
        with self.assertRaises(ValueError): self.add(baselines=['docs/architecture/BASELINE.md'])
        self.assertEqual(self.snapshot(), {})

    def test_legacy_entrypoints_rejected_without_writes(self):
        for path in ['slice.md', 'SLICES.md', 'ARCHITECTURAL_BASELINE.md', 'BASELINE.md',
                     'docs/slice.md', 'docs/ARCHITECTURAL_BASELINE.md', 'docs/architecture/BASELINE.md',
                     'SPEC.md', 'docs/RUN.md', 'docs/slices/old.md']:
            with self.subTest(path=path), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                old = root/path
                old.parent.mkdir(parents=True, exist_ok=True)
                old.write_text('# Keep this original', encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'adaptation'):
                    ps.register_slice(root, title='new', goal='outcome', module='test')
                self.assertEqual([p for p in root.rglob('*') if p.is_file()], [old])
                self.assertEqual(old.read_text(), '# Keep this original')

    def test_root_legacy_symlink_rejected_without_new_project(self):
        old = self.root/'slice.md'
        try: old.symlink_to(self.root/'missing.md')
        except OSError: self.skipTest('Symlinks unavailable')
        with self.assertRaises(ValueError): self.add()
        self.assertTrue(old.is_symlink())
        self.assertFalse((self.root/'.thinstack.json').exists())

    def test_explicit_legacy_paths_remain_canonical(self):
        r = self.add()
        (self.root/'docs/SLICES.md').rename(self.root/'slice.md')
        (self.root/'docs/architecture/BASELINE.md').rename(self.root/'ARCHITECTURAL_BASELINE.md')
        (self.root/'legacy').mkdir()
        (self.root/r['path']).rename(self.root/'legacy/TASK-009.md')
        self.edit('legacy/TASK-009.md', id='TASK-009')
        cfg = {'schema_version':1,'overview':'slice.md','records':['legacy/TASK-009.md'],
               'baselines':['ARCHITECTURAL_BASELINE.md']}
        (self.root/'.thinstack.json').write_text(json.dumps(cfg), encoding='utf-8')
        r = self.add()
        self.assertEqual(r['id'], 'TASK-010')
        self.assertEqual(r['path'], 'legacy/TASK-010.md')
        self.assertFalse((self.root/'docs/SLICES.md').exists())
        self.assertFalse((self.root/'docs/architecture/BASELINE.md').exists())
        self.assertFalse(ps.Project(self.root).inspect().issues)

    def test_numbering_preserves_padding_and_includes_cancelled(self):
        self.assertEqual(ps.next_slice_id({'TASK-009','TASK-010'}), 'TASK-011')
        r = self.add()
        self.edit(r['path'], id='S-099', stage='cancelled')
        self.assertEqual(self.add()['id'], 'S-100')

    def test_ambiguous_numbering_requires_explicit_id(self):
        self.add()
        r = self.add()
        self.edit(r['path'], id='TASK-002')
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, '--id'): self.add()
        self.assertEqual(before, self.snapshot())
        self.assertEqual(self.add(slice_id='TASK-003')['id'], 'TASK-003')

    def test_duplicate_explicit_id_rejected(self):
        self.add()
        before = self.snapshot()
        with self.assertRaises(ValueError): self.add(slice_id='S-001')
        self.assertEqual(before, self.snapshot())

    def test_non_numbered_history_not_restarted(self):
        r = self.add()
        self.edit(r['path'], id='customer-import')
        with self.assertRaisesRegex(ValueError, '--id'): self.add()
        self.assertEqual(self.add(slice_id='customer-export')['id'], 'customer-export')

    def test_no_overwrite_of_unregistered_destination(self):
        self.add()
        path = self.root/'docs/slices/S-002.md'
        path.write_text('# Not registered; do not overwrite')
        before = self.snapshot()
        with self.assertRaises(ValueError): self.add()
        self.assertEqual(before, self.snapshot())

    def test_multiple_directories_require_explicit_target(self):
        self.add()
        self.add(record_dir='work')
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, '--record-dir'): self.add()
        self.assertEqual(before, self.snapshot())
        self.assertEqual(self.add(record_dir='work')['path'], 'work/S-003.md')

    def test_path_escape_rejected(self):
        self.add()
        for kwargs in ({'record_dir':'../outside'}, {'slice_id':'../x'}, {'record_dir':'C:\\bad'}):
            before = self.snapshot()
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError): self.add(**kwargs)
            self.assertEqual(before, self.snapshot())

    def test_record_has_one_source_for_state_and_acceptance(self):
        r = self.add(acceptance=['Unique criterion'], evidence_kinds=['runtime'])
        text = (self.root/r['path']).read_text(encoding='utf-8')
        block = ps.BLOCK.search(text)
        prose = text[:block.start()] + text[block.end():]
        for repeated in ['- 阶段：', '- 依赖：', '- 批准：', 'Unique criterion']:
            self.assertNotIn(repeated, prose)
        self.edit(r['path'], stage='doing')
        ps.Project(self.root).inspect().write()
        self.assertIn('开发中', (self.root/'docs/SLICES.md').read_text(encoding='utf-8'))
        self.assertNotIn('已计划', prose)

    def test_doctor_remains_read_only(self):
        self.add()
        before = self.snapshot()
        ps.Project(self.root).inspect()
        self.assertEqual(before, self.snapshot())

    def test_sync_idempotent(self):
        self.add()
        before = self.snapshot()
        self.assertFalse(ps.Project(self.root).inspect().write())
        self.assertEqual(before, self.snapshot())

    def test_common_lock_blocks_add_and_sync(self):
        self.add()
        before = self.snapshot()
        with ps.project_lock(self.root):
            with self.assertRaises(OSError): self.add()
            with self.assertRaises(OSError): ps.Project(self.root).inspect().write()
        self.assertEqual(before, self.snapshot())

    def test_legacy_lock_is_not_deleted(self):
        path = self.root/'.thinstack-add.lock'
        path.write_text('other operation')
        with self.assertRaisesRegex(ValueError, 'Legacy'): self.add()
        self.assertEqual(path.read_text(), 'other operation')
        self.assertFalse((self.root/'.thinstack-sync.lock').exists())

    def test_stale_sync_snapshot_preserves_external_edit(self):
        r = self.add()
        p = ps.Project(self.root).inspect()
        overview = self.root/'docs/SLICES.md'
        external = overview.read_bytes() + b'\nEXTERNAL\n'
        overview.write_bytes(external)
        with self.assertRaisesRegex(ValueError, 'Concurrent'): p.write()
        self.assertEqual(overview.read_bytes(), external)
        self.assertFalse((self.root/'.thinstack-sync.lock').exists())

    def test_rollback_preserves_overview_it_did_not_write(self):
        self.add()
        before_config = (self.root/'.thinstack.json').read_bytes()
        overview = self.root/'docs/SLICES.md'
        external = overview.read_bytes() + b'\nEXTERNAL\n'
        def fail(*args, **kwargs):
            overview.write_bytes(external)
            raise OSError('injected sync failure')
        with patch.object(ps.Project, '_write_locked', fail), self.assertRaises(OSError): self.add()
        self.assertEqual(overview.read_bytes(), external)
        self.assertEqual((self.root/'.thinstack.json').read_bytes(), before_config)
        self.assertFalse((self.root/'docs/slices/S-002.md').exists())

    def test_clean_failure_rolls_back_only_own_files(self):
        self.add()
        before = self.snapshot()
        with patch.object(ps.Project, '_write_locked', side_effect=OSError('fail')), self.assertRaises(OSError): self.add()
        self.assertEqual(before, self.snapshot())

    def test_first_add_failure_cleans_its_files(self):
        with patch.object(ps.Project, '_write_locked', side_effect=OSError('fail')), self.assertRaises(OSError): self.add()
        self.assertEqual(self.snapshot(), {})

    def test_conflicting_new_record_is_preserved_with_recovery_scene(self):
        self.add()
        new = self.root/'docs/slices/S-002.md'
        def fail(*args, **kwargs):
            new.write_text('EXTERNAL changes on new file', encoding='utf-8')
            raise OSError('fail')
        with patch.object(ps.Project, '_write_locked', fail), self.assertRaisesRegex(ValueError, 'Rollback conflict'): self.add()
        self.assertEqual(new.read_text(), 'EXTERNAL changes on new file')
        self.assertIn('docs/slices/S-002.md', json.loads((self.root/'.thinstack.json').read_text())['records'])
        self.assertFalse((self.root/'.thinstack-sync.lock').exists())

    def test_changed_config_not_replaced_by_old_snapshot(self):
        self.add()
        cfg = self.root/'.thinstack.json'
        external = b'{"external": "keep this"}\n'
        def fail(*args, **kwargs):
            cfg.write_bytes(external)
            raise OSError('fail')
        with patch.object(ps.Project, '_write_locked', fail), self.assertRaisesRegex(ValueError, 'Rollback conflict'): self.add()
        self.assertEqual(cfg.read_bytes(), external)
        self.assertTrue((self.root/'docs/slices/S-002.md').exists())

    def test_destination_change_during_staging_preserved(self):
        self.add()
        old = ps.atomic_write
        path = self.root/'docs/slices/S-002.md'
        injected = []
        def race(target, data, **kwargs):
            # Windows temporary roots may arrive under a short-path alias.
            if target.resolve() == path.resolve():
                injected.append(True)
                target.write_bytes(b'EXTERNAL')
            return old(target, data, **kwargs)
        with patch.object(ps, 'atomic_write', race), self.assertRaises(ValueError): self.add()
        self.assertEqual(injected, [True], 'The concurrent write must actually be injected')
        self.assertEqual(path.read_bytes(), b'EXTERNAL')

    def test_after_replace_failure_is_recovered(self):
        self.add()
        before = self.snapshot()
        old = ps.atomic_write
        failed = []
        def late(target, data, **kwargs):
            old(target, data, **kwargs)
            if target.name == '.thinstack.json' and not failed:
                failed.append(True)
                raise OSError('injected failure after atomic replace')
        with patch.object(ps, 'atomic_write', late), self.assertRaises(OSError): self.add()
        self.assertEqual(before, self.snapshot())

    def test_read_failure_releases_lock(self):
        self.add()
        with patch.object(ps.Project, 'inspect', side_effect=OSError('read failed')), self.assertRaises(OSError): self.add()
        self.assertFalse((self.root/'.thinstack-sync.lock').exists())

    def test_lock_blocks_reentrant_writer_during_add(self):
        self.add()
        original = ps.Project._write_locked
        blocked = []
        def check(p, *args, **kwargs):
            try: ps.Project(self.root).inspect().write()
            except FileExistsError: blocked.append(True)
            return original(p, *args, **kwargs)
        with patch.object(ps.Project, '_write_locked', check): self.add()
        self.assertEqual(blocked, [True])

    def test_source_changed_during_staging_prevents_stale_sync(self):
        r = self.add()
        self.edit(r['path'], stage='doing')
        p = ps.Project(self.root).inspect()
        before = (self.root/'docs/SLICES.md').read_bytes()
        old = ps.atomic_write
        def race(target, data, **kwargs):
            self.edit(r['path'], stage='verify')
            return old(target, data, **kwargs)
        with patch.object(ps, 'atomic_write', race), self.assertRaisesRegex(ValueError, 'Concurrent'):
            p.write()
        self.assertEqual((self.root/'docs/SLICES.md').read_bytes(), before)
        record = ps.Project(self.root).inspect().rows[0]['record']
        self.assertEqual(record['stage'], 'verify')

    def test_second_overview_replace_failure_cleans_new_project(self):
        old = ps.atomic_write
        seen = []
        def fail_second(target, data, **kwargs):
            if target.name == 'SLICES.md':
                seen.append(True)
                if len(seen) == 2:
                    raise OSError('second overview replace failed before writing')
            return old(target, data, **kwargs)
        with patch.object(ps, 'atomic_write', fail_second), self.assertRaises(OSError): self.add()
        self.assertEqual(self.snapshot(), {})

    def test_cli_legacy_rejection_exit_two(self):
        (self.root/'slice.md').write_text('# original')
        p = subprocess.run([sys.executable, '-B', str(SCRIPT), 'add', '--root', str(self.root),
                            '--title', 't', '--goal', 'g', '--module', 'm', '--json'],
                           capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(p.returncode, 2)
        self.assertEqual(json.loads(p.stdout)['result'], 'PROJECT_ERROR')
        self.assertFalse((self.root/'docs/SLICES.md').exists())

    def test_cli_new_id_and_directory(self):
        p = subprocess.run([sys.executable, '-B', str(SCRIPT), 'add', '--root', str(self.root),
                            '--title', 't', '--goal', 'g', '--module', 'm', '--id', 'TASK-009',
                            '--record-dir', 'records', '--json'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(p.returncode, 0, p.stdout+p.stderr)
        self.assertEqual(json.loads(p.stdout)['path'], 'records/TASK-009.md')


if __name__ == '__main__':
    unittest.main()
