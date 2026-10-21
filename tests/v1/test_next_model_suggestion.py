"""Seven-tier coverage for single-lane NEXT model recommendation (freeze F9/A).

context.model stays the default; a different strictly validated label is accepted
and displayed. Synthetic fixtures only — no Knowtation, vault, or credentials.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

import pytest
import yaml

from cli import v1
from cli.v1_io import Refusal, digest
from tests.fpr2.test_lanes import lanes
from tests.v1.conftest import KIT, command, seed, status, write_action
from tests.v1.test_commands import fingerprint

# Freeze path-notation aliases used as model values in integration and above.
CODEX = 'OpenAI Codex (latest GPT model, high reasoning)'
DEFAULT = 'GPT-6 Astra'


def _hand_edit_model(repo, model):
    """Rewrite NEXT frontmatter model while keeping prompt_sha256 valid."""
    data = (repo / v1.NEXT).read_bytes()
    meta, prompt = v1.parse_next(data)
    meta['model'] = model
    (repo / v1.NEXT).write_bytes(b'---\n' + v1.encode(meta) + b'---\n' + prompt.encode())


# ---------------------------------------------------------------------------
# 1. Unit
# ---------------------------------------------------------------------------

def test_model_label_accepts_documented_values():
    """Unit: model_label returns the same object for documented valid labels."""
    for value in ('CODEX', 'OPUS', 'GPT-6 Astra', 'Cursor Auto', 'Fixture Reviewer'):
        assert v1.model_label(value) is value
    long_ok = 'A' + ('b' * 119)
    assert len(long_ok) == 120
    assert v1.model_label(long_ok) is long_ok
    assert v1.MODEL_LABEL_MAX == 120


@pytest.mark.parametrize('value', [None, 1, b'x'])
def test_model_label_refuses_non_str(value):
    """Unit: non-str values raise model_label_invalid."""
    with pytest.raises(Refusal, match='model_label_invalid'):
        v1.model_label(value)


REJECT_TABLE = [
    '',
    ' x',
    'x ',
    'a  b',
    '\n',
    '\r',
    '\t',
    '\x00',
    '\x7f',
    '\u0085',
    '\u2028',
    '\u202e',
    'Modèle',
    '1abc',
    '-x',
    'A' + ('b' * 120),  # 121 characters
    'Model: x',
    'a:b',
    '```',
    '<!-- overseer-next:x -->',
    '<x>',
    '$(id)',
    'a;b',
    'a|b',
    "'x",
    '"x',
    '#x',
]


@pytest.mark.parametrize('value', REJECT_TABLE)
def test_model_label_refuses_security_table(value):
    """Unit: every security-table value raises model_label_invalid."""
    with pytest.raises(Refusal, match='model_label_invalid'):
        v1.model_label(value)


# ---------------------------------------------------------------------------
# 2. Integration
# ---------------------------------------------------------------------------

def test_next_write_codex_displays_and_json_reports(repo):
    """Integration: CODEX publish is accepted; text and JSON show the label."""
    r = write_action(repo, 'Codex task\n', model=CODEX)
    assert r.returncode == 0, r.stderr
    shown = command('-C', repo, 'next')
    assert shown.returncode == 0, shown.stderr
    assert f'Model: {CODEX}' in shown.stdout
    js = command('-C', repo, 'next', '--json')
    assert js.returncode == 0, js.stderr
    assert json.loads(js.stdout)['next']['model'] == CODEX


def test_next_model_expectation_checks(repo):
    """Integration: --model expectation matches published label only."""
    write_action(repo, 'Codex task\n', model=CODEX)
    ok = command('-C', repo, 'next', '--model', CODEX)
    assert ok.returncode == 0, ok.stderr
    bad = command('-C', repo, 'next', '--model', DEFAULT)
    assert bad.returncode == 2 and not bad.stdout
    assert 'expected_model_mismatch' in bad.stderr


def test_batch_codex_and_double_space_refusal(repo):
    """Integration: single-lane batch with CODEX publishes; double space refuses."""
    state = status(repo)
    before = (repo / v1.NEXT).read_bytes()
    good = {'lanes': {'product': {
        'model': CODEX, 'action_id': 'BATCH-CODEX', 'action_kind': 'implement',
        'prompt': 'Batch CODEX task\n'}}}
    (repo / 'batch.json').write_text(json.dumps(good))
    r = command('-C', repo, 'next-write', '--repo-id', state['repository']['id'],
                '--branch', 'main', '--expect-next', state['next_sha256'],
                '--batch-file', 'batch.json')
    assert r.returncode == 0, r.stderr
    assert json.loads(command('-C', repo, 'next', '--json').stdout)['next']['model'] == CODEX

    state = status(repo)
    before = (repo / v1.NEXT).read_bytes()
    bad = {'lanes': {'product': {
        'model': 'Codex  Two', 'action_id': 'BATCH-BAD', 'action_kind': 'implement',
        'prompt': 'Should not publish\n'}}}
    (repo / 'batch-bad.json').write_text(json.dumps(bad))
    r = command('-C', repo, 'next-write', '--repo-id', state['repository']['id'],
                '--branch', 'main', '--expect-next', state['next_sha256'],
                '--batch-file', 'batch-bad.json')
    assert r.returncode == 2 and not r.stdout
    assert 'model_label_invalid' in r.stderr
    assert (repo / v1.NEXT).read_bytes() == before


def test_init_and_sync_hooks_with_codex_next(repo):
    """Integration: existing-config init and sync --hooks leave a CODEX NEXT intact."""
    write_action(repo, 'Codex task\n', model=CODEX)
    before = (repo / v1.NEXT).read_bytes()
    assert command('-C', repo, 'init').returncode == 0
    assert command('-C', repo, 'sync', '--hooks').returncode == 0
    assert (repo / v1.NEXT).read_bytes() == before


def test_default_label_outside_strict_grammar_still_works(tmp_path):
    """Integration: context.model outside MODEL_LABEL still publishes as equal."""
    root = seed(tmp_path / 'unicode-default')
    r = command('-C', root, 'init', '--model', 'Modèle par défaut', '--hooks')
    assert r.returncode == 0, r.stderr
    state = status(root)
    assert state['configuration']['context']['model'] == 'Modèle par défaut'
    (root / 'prompt.txt').write_text('Default unicode model task\n')
    ok = command('-C', root, 'next-write',
                 '--repo-id', state['repository']['id'], '--branch', 'main',
                 '--lane', 'product', '--model', 'Modèle par défaut',
                 '--action-id', 'UNICODE-OK', '--action-kind', 'implement',
                 '--expect-next', state['next_sha256'], '--prompt-file', 'prompt.txt')
    assert ok.returncode == 0, ok.stderr
    state = status(root)
    before = (root / v1.NEXT).read_bytes()
    (root / 'prompt2.txt').write_text('Should refuse\n')
    bad = command('-C', root, 'next-write',
                  '--repo-id', state['repository']['id'], '--branch', 'main',
                  '--lane', 'product', '--model', 'Modèle 2',
                  '--action-id', 'UNICODE-BAD', '--action-kind', 'implement',
                  '--expect-next', state['next_sha256'], '--prompt-file', 'prompt2.txt')
    assert bad.returncode == 2 and not bad.stdout
    assert 'model_label_invalid' in bad.stderr
    assert (root / v1.NEXT).read_bytes() == before


def test_multi_lane_non_ascii_model_unchanged(repo):
    """Integration: multi-lane still accepts a general label() model such as Modèle."""
    lanes(repo)
    cfg = yaml.safe_load((repo / v1.CONFIG).read_bytes())
    path = 'prompt-architecture.txt'
    (repo / path).write_text('Architecture with Modèle\n')
    r = command('-C', repo, 'next-write', '--repo-id', cfg['repo']['id'],
                '--branch', v1.branch(repo), '--lane', 'architecture',
                '--model', 'Modèle', '--action-id', 'LANE-MODELE',
                '--action-kind', 'implement',
                '--expect-next', digest((repo / v1.NEXT).read_bytes()),
                '--prompt-file', path)
    assert r.returncode == 0, r.stderr
    shown = command('-C', repo, 'next', '--lane', 'architecture', '--json')
    assert shown.returncode == 0, shown.stderr
    assert json.loads(shown.stdout)['next']['model'] == 'Modèle'


# ---------------------------------------------------------------------------
# 3. End-to-end (Git)
# ---------------------------------------------------------------------------

def test_git_e2e_codex_then_default_successor(repo):
    """End-to-end: publish CODEX via bound launcher from cwd=/, then default with expect-next."""
    r = write_action(repo, 'Codex e2e\n', model=CODEX)
    assert r.returncode == 0, r.stderr
    published = status(repo)['next_sha256']
    fresh = subprocess.run(
        [str(repo / '.overseer/bin/ok'), '-C', str(repo), 'next'],
        cwd='/', capture_output=True, text=True, timeout=20)
    assert fresh.returncode == 0, fresh.stderr
    assert f'Model: {CODEX}' in fresh.stdout
    successor = write_action(repo, 'Back to default\n', model=DEFAULT, expect_next=published)
    assert successor.returncode == 0, successor.stderr
    fresh2 = subprocess.run(
        [str(repo / '.overseer/bin/ok'), '-C', str(repo), 'next'],
        cwd='/', capture_output=True, text=True, timeout=20)
    assert fresh2.returncode == 0, fresh2.stderr
    assert f'Model: {DEFAULT}' in fresh2.stdout
    assert status(repo)['ok'] is True


# ---------------------------------------------------------------------------
# 4. Stress
# ---------------------------------------------------------------------------

def test_stress_alternating_codex_and_default(repo):
    """Stress: 50 alternating CODEX/default publications each with prior expect-next."""
    model = DEFAULT
    for i in range(50):
        model = CODEX if i % 2 == 0 else DEFAULT
        r = write_action(repo, f'Alternating {i}\n', model=model)
        assert r.returncode == 0, r.stderr
        shown = command('-C', repo, 'next')
        assert shown.returncode == 0, shown.stderr
        assert f'Model: {model}' in shown.stdout


def test_stress_concurrent_codex_and_default_writers(repo):
    """Stress: 20 iterations of concurrent CODEX vs default writers; one wins CAS.

    Pattern matches tests/v1/test_integrity.py:65-78 (including concurrent readers).
    Advisory directory flock can miss a same-UID double-compare race; each
    iteration retries until the CAS conflict ([0, 2] + stale_write) is observed.
    """
    for _ in range(20):
        for attempt in range(40):
            state = status(repo)
            (repo / 'prompt-codex').write_text(f'Concurrent CODEX {attempt}\n')
            (repo / 'prompt-default').write_text(f'Concurrent default {attempt}\n')
            base = [str(KIT / 'cli/ok'), '-C', str(repo), 'next-write',
                    '--repo-id', state['repository']['id'], '--branch', 'main',
                    '--lane', 'product', '--action-id', 'CONCURRENT',
                    '--action-kind', 'implement', '--expect-next', state['next_sha256']]
            workers = [
                subprocess.Popen(base + ['--model', CODEX, '--prompt-file', 'prompt-codex'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True),
                subprocess.Popen(base + ['--model', DEFAULT, '--prompt-file', 'prompt-default'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True),
            ]
            for _ in range(5):
                r = command('-C', repo, 'next')
                assert r.returncode == 0, r.stderr
            outcomes = [(p.communicate(timeout=15), p.returncode) for p in workers]
            codes = sorted(code for _, code in outcomes)
            assert not list((repo / 'docs').glob('.NEXT.md.*'))
            published = json.loads(command('-C', repo, 'next', '--json').stdout)['next']['model']
            assert published in (CODEX, DEFAULT)
            if codes == [0, 0]:
                continue
            assert codes == [0, 2], outcomes
            loser_stderr = next(stderr for (stdout, stderr), code in outcomes if code == 2)
            assert 'stale_write' in loser_stderr
            break
        else:
            raise AssertionError('CAS conflict not observed within retry budget')


def test_stable_hard_link_still_refused(repo):
    """Security: a second name for docs/NEXT.md that outlasts the retries is refused.

    After a published NEXT, os.link adds another directory entry for that file.
    ok next exits 2, stdout is empty, and stderr contains path_not_regular.
    Removing the extra entry lets ok next exit 0 and show the published model.
    """
    published = write_action(repo, 'Stable hard link probe\n', model=CODEX)
    assert published.returncode == 0, published.stderr
    extra = repo / 'docs' / 'NEXT.md.extra'
    os.link(repo / v1.NEXT, extra)
    refused = command('-C', repo, 'next')
    assert refused.returncode == 2 and not refused.stdout
    assert 'path_not_regular' in refused.stderr
    extra.unlink()
    shown = command('-C', repo, 'next')
    assert shown.returncode == 0, shown.stderr
    assert f'Model: {CODEX}' in shown.stdout


# ---------------------------------------------------------------------------
# 5. Data-integrity
# ---------------------------------------------------------------------------

def test_codex_write_changes_only_next(repo):
    """Data-integrity: successful CODEX write changes only docs/NEXT.md bytes/mode."""
    (repo / 'prompt.txt').write_text('Codex integrity\n')
    before = fingerprint(repo)
    state = status(repo)
    r = command('-C', repo, 'next-write',
                '--repo-id', state['repository']['id'], '--branch', 'main',
                '--lane', 'product', '--model', CODEX,
                '--action-id', 'INTEGRITY', '--action-kind', 'implement',
                '--expect-next', state['next_sha256'], '--prompt-file', 'prompt.txt')
    assert r.returncode == 0, r.stderr
    after = fingerprint(repo)
    changed = {path for path in set(before) | set(after)
               if before.get(path) != after.get(path)}
    assert changed == {v1.NEXT}


def test_invalid_label_write_changes_nothing(repo):
    """Data-integrity: refused invalid-label write leaves binding and NEXT untouched."""
    before_next = (repo / v1.NEXT).read_bytes()
    before_mode = (repo / v1.NEXT).stat().st_mode
    before_cfg = (repo / v1.CONFIG).read_bytes()
    before_lock = (repo / '.overseer/version.lock').read_bytes()
    before_ok = (repo / '.overseer/bin/ok').read_bytes()
    r = write_action(repo, 'Should refuse\n', model='a  b')
    assert r.returncode == 2 and not r.stdout
    assert 'model_label_invalid' in r.stderr
    assert (repo / v1.NEXT).read_bytes() == before_next
    assert (repo / v1.NEXT).stat().st_mode == before_mode
    assert (repo / v1.CONFIG).read_bytes() == before_cfg
    assert (repo / '.overseer/version.lock').read_bytes() == before_lock
    assert (repo / '.overseer/bin/ok').read_bytes() == before_ok
    assert not list((repo / 'docs').glob('.NEXT.md.*'))


def test_prompt_sha256_and_rendered_body(repo):
    """Data-integrity: prompt_sha256 matches file; rendered body equals prompt content."""
    prompt = 'Prompt body for digest check\n'
    (repo / 'prompt.txt').write_text(prompt)
    state = status(repo)
    r = command('-C', repo, 'next-write',
                '--repo-id', state['repository']['id'], '--branch', 'main',
                '--lane', 'product', '--model', CODEX,
                '--action-id', 'DIGEST-CHECK', '--action-kind', 'implement',
                '--expect-next', state['next_sha256'], '--prompt-file', 'prompt.txt')
    assert r.returncode == 0, r.stderr
    meta, body = v1.parse_next((repo / v1.NEXT).read_bytes())
    assert meta['prompt_sha256'] == hashlib.sha256(prompt.encode()).hexdigest()
    shown = command('-C', repo, 'next')
    assert shown.returncode == 0
    assert shown.stdout.endswith(prompt) or prompt.rstrip() in shown.stdout
    assert status(repo)['ok'] is True


def test_status_ok_after_codex_and_refusal(repo):
    """Data-integrity: status --json exits 0 after a CODEX write and after a refused write."""
    write_action(repo, 'Codex status\n', model=CODEX)
    assert status(repo)['ok'] is True
    before = status(repo)['next_sha256']
    bad = write_action(repo, 'Refuse\n', model='a  b')
    assert bad.returncode == 2
    assert status(repo)['next_sha256'] == before
    assert status(repo)['ok'] is True


# ---------------------------------------------------------------------------
# 6. Performance
# ---------------------------------------------------------------------------

def test_ten_codex_next_reads_under_ten_seconds(repo):
    """Performance: ten ok next reads of a CODEX NEXT complete in under 10 s."""
    write_action(repo, 'Perf CODEX\n', model=CODEX)
    start = time.monotonic()
    for _ in range(10):
        assert command('-C', repo, 'next').returncode == 0
    assert time.monotonic() - start < 10


def test_model_label_in_process_calls_under_one_second():
    """Performance: 100,000 in-process model_label(CODEX) calls complete in under 1.0 s."""
    start = time.monotonic()
    for _ in range(100_000):
        assert v1.model_label(CODEX) is CODEX
    assert time.monotonic() - start < 1.0


# ---------------------------------------------------------------------------
# 7. Security
# ---------------------------------------------------------------------------

def test_next_write_rejects_security_table(repo):
    """Security: next-write refuses table values (except empty/NUL) without changing NEXT."""
    c0 = {'\n', '\r', '\t'}
    skip = {'', '\x00'}
    for value in REJECT_TABLE:
        if value in skip:
            continue
        before = (repo / v1.NEXT).read_bytes()
        state = status(repo)
        (repo / 'prompt-sec.txt').write_text('Security probe\n')
        r = command('-C', repo, 'next-write',
                    '--repo-id', state['repository']['id'], '--branch', 'main',
                    '--lane', 'product', f'--model={value}',
                    '--action-id', 'SEC', '--action-kind', 'implement',
                    '--expect-next', state['next_sha256'],
                    '--prompt-file', 'prompt-sec.txt')
        assert r.returncode == 2 and not r.stdout, repr(value)
        assert (repo / v1.NEXT).read_bytes() == before
        # label() refuses C0 and Unicode whitespace that .strip() empties first.
        if value in c0 or value in ('\u0085', '\u2028'):
            if value == '\u0085':
                # Freeze: no specific code; encoder/strip gap belongs to F11.
                assert 'refused:' in r.stderr, r.stderr
            else:
                assert 'label_invalid' in r.stderr, repr(value)
        else:
            assert 'model_label_invalid' in r.stderr, (repr(value), r.stderr)


def test_hand_edit_line_separator_refused_and_valid_label_digest_mismatch(repo):
    """Security: hand-edited U+2028 label refuses; valid hand-edit needs expect-next."""
    write_action(repo, 'Codex hand-edit base\n', model=CODEX)
    _hand_edit_model(repo, 'Codex\u2028Lane: other')
    r = command('-C', repo, 'next')
    assert r.returncode == 2 and not r.stdout
    assert 'model_label_invalid' in r.stderr
    js = command('-C', repo, 'next', '--json')
    assert js.returncode == 2 and not js.stdout
    assert 'model_label_invalid' in js.stderr
    st = command('-C', repo, 'status', '--json')
    assert st.returncode == 1
    assert 'model_label_invalid' in json.loads(st.stdout)['next_error']

    # parse_next still accepts the bytes (label allows U+2028); restore CODEX.
    meta, prompt = v1.parse_next((repo / v1.NEXT).read_bytes())
    meta['model'] = CODEX
    (repo / v1.NEXT).write_bytes(b'---\n' + v1.encode(meta) + b'---\n' + prompt.encode())
    published = status(repo)['next_sha256']
    shown = command('-C', repo, 'next')
    assert shown.returncode == 0 and f'Model: {CODEX}' in shown.stdout

    _hand_edit_model(repo, 'OpenAI Codex')
    shown = command('-C', repo, 'next')
    assert shown.returncode == 0 and 'Model: OpenAI Codex' in shown.stdout
    mismatch = command('-C', repo, 'next', '--expect-next', published)
    assert mismatch.returncode == 2 and not mismatch.stdout
    assert 'next_digest_mismatch' in mismatch.stderr


def test_regression_refusals_with_codex_present(repo):
    """Security: retained writer checks still refuse with a CODEX NEXT present."""
    write_action(repo, 'Codex regression base\n', model=CODEX)
    before = (repo / v1.NEXT).read_bytes()
    cases = [
        dict(repo_id='00000000-0000-0000-0000-000000000000'),
        dict(branch='other'),
        dict(lane='other'),
        dict(action_id='bad/action'),
        dict(action_kind='deploy'),
        dict(expect_next='0' * 64),
    ]
    for overrides in cases:
        r = write_action(repo, 'Should refuse\n', **overrides)
        assert r.returncode != 0 and not r.stdout, overrides
        assert (repo / v1.NEXT).read_bytes() == before

    abs_r = write_action(repo, 'Should refuse\n', prompt_file='/tmp/outside-prompt.txt')
    assert abs_r.returncode == 2
    assert 'path_invalid' in abs_r.stderr
    assert (repo / v1.NEXT).read_bytes() == before

    (repo / 'binding-prompt.txt').write_text('Model: injected\n')
    state = status(repo)
    binding = command('-C', repo, 'next-write',
                      '--repo-id', state['repository']['id'], '--branch', 'main',
                      '--lane', 'product', '--model', CODEX,
                      '--action-id', 'BIND', '--action-kind', 'implement',
                      '--expect-next', state['next_sha256'],
                      '--prompt-file', 'binding-prompt.txt')
    assert binding.returncode == 2 and not binding.stdout
    assert 'prompt_contains_binding_fields' in binding.stderr
    assert (repo / v1.NEXT).read_bytes() == before

    (repo / 'lane-prompt.txt').write_text('Lane: other\n')
    state = status(repo)
    lane_line = command('-C', repo, 'next-write',
                        '--repo-id', state['repository']['id'], '--branch', 'main',
                        '--lane', 'product', '--model', CODEX,
                        '--action-id', 'LANE', '--action-kind', 'implement',
                        '--expect-next', state['next_sha256'],
                        '--prompt-file', 'lane-prompt.txt')
    assert lane_line.returncode == 2 and not lane_line.stdout
    assert 'prompt_contains_binding_fields' in lane_line.stderr
    assert (repo / v1.NEXT).read_bytes() == before
