"""Curate only completed disposable observations; preserve every original byte."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import plistlib
import re
import stat

BASE = Path('/private/tmp/overseer-fpr5-host-platform-20261015-0crxbk22')
REPO = Path('/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014')
DEST = REPO / 'docs/validation/fpr5-interactive/observations'
META = Path(__file__).parent
RUNS = [
    'owner-observation-desktop-g1lukv03',
    'owner-observation-desktop-0pkcm8sj',
    'owner-observation-cursor-p7_1rhzy',
    'c-n68k5cn1',
]
PREPARATIONS = [
    'owner-desktop-600-preparation-ne7i2ulw',
    'cursor-short-preparation-8ictvmw7',
]
CREDENTIAL_WORDS = re.compile(r'authorization|credential|password|secret|token|cookie|bearer', re.I)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_info(path):
    assert path.is_file() and not path.is_symlink(), path
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'mode': format(stat.S_IMODE(path.stat().st_mode), '04o'), 'sha256': digest(raw)}


def write_json(name, value):
    path = META / name
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    return path


def main():
    assert not DEST.exists(), 'Never overwrite an existing durable observation tree'
    old_inventory = REPO / 'docs/validation/fpr5-acceptance/host-platform/INVENTORY.json'
    old_inventory_hash = digest(old_inventory.read_bytes())
    results = {}
    for name in RUNS:
        result = json.loads((BASE / name / 'result.json').read_text())
        assert result['remaining_group_before_fallback'] == '', name
        assert result['next_unchanged'] is True, name
        results[name] = result
    forced_close = json.loads((BASE / 'c-n68k5cn1/forced-close-after-keychain-gate.json').read_text())
    assert forced_close['remaining_group'] == ''
    assert results['c-n68k5cn1']['exit'] == -9

    app = Path('/Applications/Cursor.app/Contents')
    version = plistlib.loads((app / 'Info.plist').read_bytes())['CFBundleShortVersionString']
    workbench = app / 'Resources/app/out/vs/workbench/workbench.desktop.main.js'
    source = workbench.read_bytes()
    expected = 'ed6922a7a86c8c448a46aa39af0c931580da162770fe406a0d41737290e637d9'
    assert version == '3.24.18' and digest(source) == expected
    locations = []
    patterns = [
        ('new_chat_tab_action', 'id:bse,title:{value:"New Chat Tab",original:"New Chat Tab"}', 420),
        ('session_start_dispatch_during_composer_creation', 'this.cursorHooksService.executeHookForStep(Lu.sessionStart,', 540),
        ('stop_hook_at_turn_end', 'async triggerStopHook(e,t)', 850),
        ('stop_followup_may_submit_another_turn', 'this.submitChatMaybeAbortCurrent(n,u,{skipClearInput:!0,skipFocusAfterSubmission:!0,isAutoFollowupFromStopHook:!0})', 160),
        ('closing_chat_dispatches_session_end', 'fireSessionEndHook(e,"user_close")', 160),
        ('hooks_output_channel_label', 'label:"Hooks",log:!1', 80),
    ]
    for label, needle, length in patterns:
        offset = source.find(needle.encode())
        assert offset >= 0, label
        locations.append({'meaning': label, 'byte_offset_zero_based': offset,
                          'snippet_utf8': source[offset:offset + length].decode('utf-8', errors='replace')})
    source_notes = write_json('cursor-source-notes.json', {
        'kind': 'Static inspection of installed Cursor source; not lifecycle acceptance',
        'cursor_version': version,
        'source': file_info(workbench),
        'offset_convention': 'Zero-based byte offset in exact SHA-256 pinned workbench file; not Unicode character offsets',
        'references': locations,
        'source_supported_interpretation': {
            'sessionStart': 'New Chat Tab creates a composer and its creation path dispatches sessionStart before explicit model submission; offline onboarding accessibility was not demonstrated.',
            'stop': 'triggerStopHook is tied to a model turn ending (completed, aborted or error), not closing the window. No permitted offline UI operation was established to deliver this event.',
            'sessionEnd': 'Closing a chat dispatches sessionEnd, a distinct event not configured as the pilot stop hook.',
            'followup_message': 'The generated hook returns this field; Cursor stop handling may submit it as another model turn. Do not invoke a model turn under current restrictions.',
        },
        'possible_start_only_owner_steps': ['Use only the approved isolated disposable pilot window.', 'Cmd+Shift+P -> New Chat Tab; leave prompt empty and do not submit.', 'View -> Output -> Hooks.', 'Stop at any sign-in, keychain or provider gate; do not change account/keychain/network settings.'],
        'required_actual_receipt': {
            'event': 'sessionStart or stop, each separately',
            'command': 'Exact matching generated script in the disposable pilot .cursor/hooks directory',
            'execution': 'Actual command execution with exit code 0; input includes correct hook_event_name, Cursor version, conversation/session identity and disposable workspace_roots',
            'output': 'Successful additional_context and followup_message containing the canonical bound NEXT output',
            'insufficient': ['Loaded hooks configuration', 'Hook event requested without command success/output', 'workspaceOpen', 'Closing a chat or window'],
        },
        'observed_acceptance': {'sessionStart': 'not demonstrated', 'stop': 'not demonstrated'},
        'no_app_launch_or_source_change_in_static_inspection': True,
    })

    log_scan = []
    markers = ['Hook step requested: sessionStart', 'Hook step requested: stop',
               'session-start-next.sh', 'session-end-closeout.sh', 'INPUT:', 'OUTPUT:', 'exit code: 0']
    for name in RUNS[2:]:
        run = BASE / name
        logs = [run / 'host.log'] + sorted((run / 'profile/logs').rglob('*.log'))
        records = []
        for path in logs:
            raw = path.read_bytes()
            records.append({'source': file_info(path), 'marker_counts': {m: raw.count(m.encode()) for m in markers}})
        log_scan.append({'run': name,
                         'hook_channel_logs': [str(p) for p in (run / 'profile/logs').rglob('*') if p.is_file() and 'cursor.hooks' in p.name],
                         'logs': records})
    scan_file = write_json('cursor-log-scan.json', {
        'kind': 'Post-close exact marker scan of the two new isolated Cursor runs; absence is not acceptance',
        'markers': markers, 'runs': log_scan,
        'interpretation': 'No actual sessionStart/stop command receipts were found. The long directory run exited with socket EINVAL; the short directory run encountered the owner-observed keychain gate and required forced cleanup.',
    })

    desktop = BASE / 'owner-observation-desktop-0pkcm8sj'
    observed = (desktop / 'user-desktop-next.txt').read_text()
    bound = json.loads((desktop / 'bound-next-at-observation.json').read_text())['rendered']
    action_blocks = lambda text: re.findall(r'```text\n(.*?)```', text, flags=re.S)
    comparison = {
        'kind': 'Coordinator comparison of owner-pasted desktop text against saved bound NEXT; not independent adjudication',
        'owner_paste': file_info(desktop / 'user-desktop-next.txt'),
        'bound_next_record': file_info(desktop / 'bound-next-at-observation.json'),
        'action_block_count': len(action_blocks(observed)),
        'action_blocks_exact_match': action_blocks(observed) == action_blocks(bound),
        'all_nonempty_lines_match': [s for s in observed.splitlines() if s.strip()] == [s for s in bound.splitlines() if s.strip()],
        'whole_string_byte_identical': observed.encode() == bound.encode(),
        'visual_evidence': 'Owner screenshot metadata and observation are in the run user-observation.json; screenshot pixels intentionally remain external.',
    }
    assert comparison['action_block_count'] == 2 and comparison['action_blocks_exact_match'] and comparison['all_nonempty_lines_match']
    comparison_file = write_json('desktop-text-comparison.json', comparison)
    check_file = write_json('curation-checks.json', {
        'kind': 'Evidence curator verification; no independent acceptance certification',
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'completed_run_results': results,
        'cursor_forced_cleanup_authority': str(BASE / 'c-n68k5cn1/forced-close-after-keychain-gate.json'),
        'cursor_normal_shutdown_pass': False,
        'curator_extra_process_check': 'Attempted read-only /bin/ps through Python, denied by execution sandbox with PermissionError errno 1. No escalation or process changes performed. Closure relies on saved launcher/final cleanup records and parent verified empty process group.',
        'old_host_platform_inventory_sha256_before': old_inventory_hash,
        'original_logs_are_not_modified': True,
        'network_or_app_launches_performed_by_curator': False,
    })

    selection = []
    for name in RUNS + PREPARATIONS:
        for path in sorted((BASE / name).iterdir()):
            if path.is_file() and path.suffix in {'.json', '.log', '.py', '.txt'}:
                selection.append((path, Path(name) / path.name))
    for name in RUNS[2:]:
        log_root = BASE / name / 'profile/logs'
        for path in sorted(log_root.rglob('*.log')):
            selection.append((path, Path(name) / 'client-logs' / path.relative_to(log_root)))
    for name in ['owner_observe.py', 'owner-observe-script-validation.json']:
        selection.append((BASE / name, Path('original-helper') / name))
    for path in [source_notes, scan_file, comparison_file, check_file, Path(__file__)]:
        selection.append((path, Path(path.name)))

    DEST.mkdir(parents=True, exist_ok=False)
    copied = []
    originals = []
    for source_path, relative in selection:
        info = file_info(source_path)
        raw = source_path.read_bytes()
        output = raw
        redactions = []
        if source_path.suffix == '.log':
            chunks = []
            for number, line in enumerate(raw.splitlines(keepends=True), 1):
                text = line.decode('utf-8', errors='replace')
                terms = sorted(set(m.group(0).lower() for m in CREDENTIAL_WORDS.finditer(text)))
                if terms:
                    redactions.append({'line_number_one_based': number, 'original_line_sha256': digest(line), 'keyword_matches': terms})
                    chunks.append(f'[REDACTED credential-related diagnostic line {number}; original retained locally]\n'.encode())
                else:
                    chunks.append(line)
            output = b''.join(chunks)
        target = DEST / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        assert not target.exists(), target
        target.write_bytes(output)
        os.chmod(target, int(info['mode'], 8))
        copied.append({'source': str(source_path), 'destination': relative.as_posix(),
                       'source_sha256': info['sha256'], 'source_bytes': info['bytes'], 'source_mode': info['mode'],
                       'copied_sha256': digest(output), 'copied_bytes': len(output), 'copied_mode': format(stat.S_IMODE(target.stat().st_mode), '04o'),
                       'byte_identical': raw == output, 'redactions': redactions})
        originals.append({**info, 'kind': 'original retained byte-identically', 'durable_copy': relative.as_posix()})

    screenshots = []
    for name in ['owner-observation-desktop-0pkcm8sj', 'c-n68k5cn1']:
        record = json.loads((BASE / name / 'user-observation.json').read_text())['screenshot']
        path = Path(record['path'])
        try:
            mode = format(stat.S_IMODE(path.stat().st_mode), '04o')
        except OSError:
            mode = None
        screenshots.append({'path': record['path'], 'bytes': record['bytes'], 'sha256': record['sha256'], 'mode': mode,
                            'kind': 'owner screenshot retained externally; pixels not read or copied by curator',
                            'hash_source': str(BASE / name / 'user-observation.json')})

    for entry in copied:
        source_path = Path(entry['source'])
        assert digest(source_path.read_bytes()) == entry['source_sha256'], source_path
        target = DEST / entry['destination']
        assert digest(target.read_bytes()) == entry['copied_sha256'], target
    assert digest(old_inventory.read_bytes()) == old_inventory_hash
    inventory = {
        'evidence_root': str(BASE), 'durable_root': str(DEST),
        'copied': copied, 'copied_count': len(copied),
        'externally_retained_selected_originals': originals,
        'externally_retained_screenshots': screenshots,
        'inventory_scope': 'Selected metadata/log/script observations only; no exhaustive profile/cache inventory. Every selected original remains untouched. Inventory itself excluded from its own content hashes.',
        'excluded': ['All profile data except explicitly copied application log files', 'Caches', 'Binaries', 'Screenshot pixels', 'Account/keychain data', 'Prior acceptance evidence trees'],
        'redaction_policy': {'applies_only_to': '*.log durable copies', 'case_insensitive_keywords': CREDENTIAL_WORDS.pattern,
                             'method': 'Replace the entire matching line; preserve one-based line numbering and record original line SHA-256. Broad keyword match is conservative and does not assert an actual credential was present.'},
        'all_selected_original_bytes_preserved': True,
        'old_host_platform_inventory_sha256_before_and_after': old_inventory_hash,
        'no_profiles_caches_binaries_or_screenshots_copied': True,
    }
    inventory_path = DEST / 'INVENTORY.json'
    inventory_path.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'durable_root': str(DEST), 'copied_count': len(copied),
                      'redacted_files': sum(bool(e['redactions']) for e in copied),
                      'redacted_lines': sum(len(e['redactions']) for e in copied),
                      'inventory_sha256': digest(inventory_path.read_bytes()),
                      'total_copied_bytes': sum(e['copied_bytes'] for e in copied)}, indent=2))


if __name__ == '__main__':
    main()
