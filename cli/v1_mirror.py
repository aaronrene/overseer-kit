"""Controlled snapshot mirrors. Preparation is offline; delivery is explicit.

One source checkout, source main branch and Git destination pair. Only a newly
created, dedicated bare Git target or this engine's own target can be used.
Git plumbing avoids checkout filters, index state, source hooks and native export
side effects. A single correspondence record plus commit trailers supports retry.
"""
from __future__ import annotations

import base64
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
import urllib.request

from cli.v1_io import Refusal, atomic, digest, read
from cli.v1_revision import OID, bounded_run, revision, unique_json

RECORD = '.overseer/local/git-bridge.json'
MARKER = 'overseer-mirror.json'
HEX = re.compile(r'[0-9a-f]{40}\Z')
CONFIG = b'[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = true\n\thooksPath = /dev/null\n\tlogAllRefUpdates = false\n'


def packed(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def env():
    result = {k: v for k, v in os.environ.items()
              if not k.startswith(('GIT_', 'MUSE_', 'PYTHON')) and k != 'VIRTUAL_ENV'}
    result.update(PATH='/usr/bin:/bin', GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null',
                  GIT_TERMINAL_PROMPT='0', GIT_OPTIONAL_LOCKS='0', LC_ALL='C',
                  GH_HOST='github.com', GH_PROMPT_DISABLED='1',
                  GIT_AUTHOR_NAME='Overseer mirror', GIT_AUTHOR_EMAIL='mirror@example.invalid',
                  GIT_COMMITTER_NAME='Overseer mirror', GIT_COMMITTER_EMAIL='mirror@example.invalid')
    return result


def git(target, *args, data=None, optional=False):
    proc = subprocess.run(['/usr/bin/git', '--no-replace-objects', '-c', 'core.hooksPath=/dev/null',
                           '-c', 'core.fsmonitor=false', '-c', 'gc.auto=0', '-C', str(target), *args],
                          input=data, env=env(), capture_output=True, timeout=30)
    if proc.returncode and not optional:
        raise Refusal('mirror_git_failed: ' + args[0])
    return proc.stdout if not proc.returncode else b''


def head(target):
    return git(target, 'rev-parse', '--verify', 'HEAD', optional=True).decode().strip() or 'absent'


def physical(value):
    if not isinstance(value, str):
        raise Refusal('mirror_path_requires_physical_absolute_root')
    path = Path(value)
    if not path.is_absolute() or path.resolve() != path or any(p.is_symlink() for p in (path, *path.parents)):
        raise Refusal('mirror_path_requires_physical_absolute_root')
    return path


def validate_plan(plan, root, config):
    from cli.v1 import keys, KIT
    keys(plan, ('schema', 'source', 'destination', 'target', 'expected_target', 'executables'))
    keys(plan['source'], ('repo_id', 'branch', 'revision', 'hub_url'))
    keys(plan['destination'], ('url', 'repository', 'branch', 'base', 'expected_head'))
    source, dest = plan['source'], plan['destination']
    if plan['schema'] != 1 or config['vcs'] != 'muse':
        raise Refusal('mirror_requires_explicit_muse_authority')
    if source['branch'] != 'main' or not OID.fullmatch(source['revision']):
        raise Refusal('mirror_requires_approved_main_revision')
    if source['repo_id'] != config['muse']['repo_id']:
        raise Refusal('mirror_source_identity_mismatch')
    # Public staging is the tested authority. Do not bypass unresolved production trust.
    if not re.fullmatch(r'https://staging\.musehub\.ai/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', source['hub_url']):
        raise Refusal('mirror_authority_url_unsupported')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', dest['repository']):
        raise Refusal('mirror_github_repository_invalid')
    if dest['url'] != 'https://github.com/' + dest['repository'] + '.git':
        raise Refusal('mirror_destination_repository_mismatch')
    for branch in (dest['branch'], dest['base']):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_/-]*', branch) or branch.endswith('/') or '//' in branch:
            raise Refusal('mirror_git_branch_invalid')
    if dest['branch'] in {'main', 'master', dest['base']}:
        raise Refusal('mirror_requires_distribution_branch')
    for expected in (plan['expected_target'], dest['expected_head']):
        if expected != 'absent' and not HEX.fullmatch(expected):
            raise Refusal('mirror_expected_head_invalid')
    if plan['expected_target'] == 'absent' and dest['expected_head'] != 'absent':
        raise Refusal('mirror_legacy_destination_requires_reconciliation')
    ex = plan['executables']
    if not isinstance(ex, list) or any(not isinstance(p, str) for p in ex) or ex != sorted(set(ex)):
        raise Refusal('mirror_executable_policy_invalid')
    target = physical(plan['target'])
    for protected in (root, Path(config['muse']['store']), KIT):
        if target.is_relative_to(protected) or protected.is_relative_to(target):
            raise Refusal('mirror_target_overlap')
    if not target.parent.is_dir():
        raise Refusal('mirror_target_parent_missing')
    return target


def binding(plan, config):
    return {'source_root': config['repo']['root'], 'checkout_id': config['repo']['id'],
            'source_id': plan['source']['repo_id'], 'source_branch': plan['source']['branch'],
            'hub_url': plan['source']['hub_url'], 'target': plan['target'],
            'destination': {k: v for k, v in plan['destination'].items() if k != 'expected_head'}}


@contextmanager
def locked(root, target):
    handles = []
    try:
        # Lock before target creation. Physical aliases share the same directory inode.
        for path in (root, target.parent):
            fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            handles.append(fd)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise Refusal('mirror_operator_busy') from None
        yield
    finally:
        for fd in handles:
            os.close(fd)


def check_source(root, config, plan):
    state = revision(root, config)
    if (state.branch, state.head, state.source_id) != (
            plan['source']['branch'], plan['source']['revision'], plan['source']['repo_id']):
        raise Refusal('mirror_source_drift')
    python = config['muse']['runtime']['python']
    helper = Path(__file__).with_name('v1_mirror_reader.py')
    proc = bounded_run([python, '-I', '-B', str(helper), str(root), json.dumps(plan['executables'])],
                       cwd=root, env=env(), limit=48 * 1024 * 1024, timeout=30)
    if proc.returncode:
        try:
            reason = json.loads(proc.stdout, object_pairs_hook=unique_json)['error']
            if not isinstance(reason, str) or len(reason) > 300:
                raise ValueError()
        except (ValueError, KeyError, TypeError):
            reason = 'invalid reader response'
        raise Refusal('mirror_projection_refused: ' + reason)
    value = json.loads(proc.stdout, object_pairs_hook=unique_json)
    if (value['state']['runtime'] != config['muse']['runtime']
            or value['state']['head'] != state.head or value['state']['repo_id'] != state.source_id
            or value['state']['branch'] != state.branch or value['state']['root'] != str(root)
            or value['state']['store'] != config['muse']['store']):
        raise Refusal('mirror_source_changed')
    return value


def inspect_target(target, pair):
    physical(str(target))
    if not target.exists():
        return 'absent'
    if not target.is_dir() or not list(target.iterdir()):
        raise Refusal('mirror_target_not_owned')
    if read(target, MARKER, missing=True) != packed(pair):
        raise Refusal('mirror_foreign_target')
    if read(target, 'config') != CONFIG:
        raise Refusal('mirror_target_config_or_hooks_changed')
    allowed = {'HEAD', 'config', MARKER, 'objects', 'refs'}
    if set(p.name for p in target.iterdir()) - allowed:
        raise Refusal('mirror_dirty_or_hooked_target')
    for path in target.rglob('*'):
        mode = path.lstat()
        if stat.S_ISLNK(mode.st_mode) or (not stat.S_ISDIR(mode.st_mode) and
                (not stat.S_ISREG(mode.st_mode) or mode.st_nlink != 1)):
            raise Refusal('mirror_target_unsafe_path')
        rel = path.relative_to(target).as_posix()
        if path.is_dir() and rel not in {'objects', 'refs', 'refs/heads'}:
            ref_dir = 'refs/heads/' + pair['destination']['branch']
            if not re.fullmatch(r'objects/[0-9a-f]{2}', rel) and not ref_dir.startswith(rel + '/'):
                raise Refusal('mirror_foreign_directory')
        if path.is_file() and rel.startswith('refs/') and rel != 'refs/heads/' + pair['destination']['branch']:
            raise Refusal('mirror_foreign_ref_file')
        if path.is_file() and rel.startswith('objects/') and not re.fullmatch(r'objects/[0-9a-f]{2}/[0-9a-f]{38}', rel):
            raise Refusal('mirror_foreign_object_or_alternate')
    branch = pair['destination']['branch']
    if read(target, 'HEAD') != ('ref: refs/heads/' + branch + '\n').encode():
        raise Refusal('mirror_target_branch_changed')
    refs = git(target, 'for-each-ref', '--format=%(refname)').decode().splitlines()
    if set(refs) - {'refs/heads/' + branch}:
        raise Refusal('mirror_foreign_refs')
    return head(target)


def create_target(target, pair):
    # Initialize a sibling first: a killed init never leaves an ambiguous target.
    with tempfile.TemporaryDirectory(prefix='.overseer-mirror-', dir=target.parent) as name:
        stage = Path(name)
        git(stage, 'init', '--bare', '--template=', '--initial-branch=' + pair['destination']['branch'])
        (stage / 'config').write_bytes(CONFIG)
        # Git init's empty metadata directories are unnecessary for loose objects.
        (stage / 'objects/info').rmdir()
        (stage / 'objects/pack').rmdir()
        (stage / 'refs/tags').rmdir()
        (stage / MARKER).write_bytes(packed(pair))
        if target.exists():
            raise Refusal('mirror_target_appeared')
        os.rename(stage, target)


def tree(target, files):
    entries = {}
    for path, item in files.items():
        node = entries
        parts = path.split('/')
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        data = base64.b64decode(item['data'], validate=True)
        oid = git(target, 'hash-object', '-w', '--stdin', data=data).decode().strip()
        node[parts[-1]] = (item['mode'], oid)
    def write(node):
        rows = []
        for name, item in sorted(node.items()):
            mode, oid, kind = ('040000', write(item), 'tree') if isinstance(item, dict) else (*item, 'blob')
            rows.append(f'{mode} {kind} {oid}\t{name}'.encode() + b'\0')
        return git(target, 'mktree', '-z', data=b''.join(rows)).decode().strip()
    return write(entries)


def verify_tree(target, commit, files):
    found = {}
    for row in git(target, 'ls-tree', '-r', '-z', commit).split(b'\0'):
        if not row:
            continue
        meta, path = row.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        path = path.decode()
        if kind != 'blob' or path not in files or mode != files[path]['mode']:
            raise Refusal('mirror_tree_paths_or_modes_mismatch')
        content = git(target, 'cat-file', 'blob', oid)
        if content != base64.b64decode(files[path]['data'], validate=True):
            raise Refusal('mirror_tree_bytes_mismatch')
        found[path] = True
    if set(found) != set(files):
        raise Refusal('mirror_tree_paths_mismatch')


def correspondence(target, commit, plan, plan_hash, files):
    if commit == 'absent':
        return False
    message = git(target, 'show', '-s', '--format=%B', commit).decode()
    trailers = f'Muse-Source: {plan["source"]["revision"]}\nOverseer-Mirror-Plan: {plan_hash}\n'
    if not message.endswith(trailers + '\n'):
        return False
    parents = git(target, 'show', '-s', '--format=%P', commit).decode().strip()
    if parents != ('' if plan['expected_target'] == 'absent' else plan['expected_target']):
        raise Refusal('mirror_commit_parent_mismatch')
    verify_tree(target, commit, files)
    return True


def save_record(root, old, pair, plan, plan_hash, commit):
    record = {'binding': pair, 'last_export': {'muse_branch': plan['source']['branch'],
              'muse_commit_id': plan['source']['revision'], 'git_remote': plan['destination']['url'],
              'git_ref': plan['destination']['branch'], 'git_sha': commit, 'plan_sha256': plan_hash}}
    data = packed(record)
    if data != old:
        atomic(root, RECORD, data, expected='absent' if old is None else digest(old))


def execute(root, config, original, plan, plan_hash, operation, transport=None):
    target = validate_plan(plan, root, config)
    result = {'ok': False, 'repository': config['repo'], 'source': plan['source'],
              'target': str(target), 'destination': plan['destination'], 'plan_sha256': plan_hash,
              'export': 'not_prepared', 'push': 'not_attempted', 'pr': 'not_attempted',
              'authority': 'approved_input_not_checked_offline'}
    with locked(root, target):
        try:
            pair = binding(plan, config)
            old = read(root, RECORD, missing=True)
            if old and json.loads(old)['binding'] != pair:
                raise Refusal('mirror_pair_changed_requires_reconciliation')
            observed = inspect_target(target, pair)
            projection = check_source(root, config, plan)
            files = projection['files']
            result.update(excluded=projection['excluded'], files=len(files),
                          directories_omitted=projection['directories_omitted'])
            already = observed != 'absent' and correspondence(target, observed, plan, plan_hash, files)
            if not already and observed != plan['expected_target']:
                raise Refusal('mirror_target_head_drift')
            if not already and operation != 'prepare':
                raise Refusal('mirror_preparation_required')
            if not already:
                if observed == 'absent' and target.exists():
                    # Only an owned, unborn target left by an interrupted prepare.
                    inspect_target(target, pair)
                elif observed == 'absent':
                    create_target(target, pair)
                else:
                    if not old or json.loads(old)['last_export']['git_sha'] != observed:
                        raise Refusal('mirror_target_mapping_mismatch')
                    # Refuse legacy/foreign content instead of sweeping it away.
                    previous_plan = json.loads(old)['last_export']['plan_sha256']
                    message = git(target, 'show', '-s', '--format=%B', observed).decode()
                    if f'Overseer-Mirror-Plan: {previous_plan}\n' not in message:
                        raise Refusal('mirror_target_correspondence_missing')
                new_tree = tree(target, files)
                same_tree = observed != 'absent' and git(target, 'rev-parse', observed + '^{tree}').decode().strip() == new_tree
                message = f'Mirror approved Muse snapshot\n\nMuse-Source: {plan["source"]["revision"]}\nOverseer-Mirror-Plan: {plan_hash}\n'
                parents = [] if observed == 'absent' else ['-p', observed]
                commit = git(target, 'commit-tree', new_tree, *parents, data=message.encode()).decode().strip()
                verify_tree(target, commit, files)
                # Recheck immutable source, working projection, config and target before the CAS.
                if check_source(root, config, plan) != projection or read(root, '.overseer/config.yaml') != original:
                    raise Refusal('mirror_source_or_config_changed')
                if inspect_target(target, pair) != observed:
                    raise Refusal('mirror_target_changed_before_commit')
                git(target, 'update-ref', 'refs/heads/' + plan['destination']['branch'], commit,
                    '0' * 40 if observed == 'absent' else observed)
                result['export'] = 'mapped_no_content_change' if same_tree else 'prepared'
                observed = commit
            else:
                result['export'] = 'no_change_verified'
            result['git_head'] = observed
            # Recover an interrupted record write using exact tree, parent and trailers.
            if not correspondence(target, observed, plan, plan_hash, files):
                raise Refusal('mirror_correspondence_failed')
            if operation != 'verify':
                save_record(root, old, pair, plan, plan_hash, observed)
            if operation == 'deliver':
                if transport is None:
                    raise Refusal('mirror_delivery_transport_missing')
                deliver(result, transport, lambda: recheck(root, config, original, plan, pair, projection, observed))
            else:
                result['ok'] = True
        except (Refusal, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
            result['error'] = str(exc) if isinstance(exc, Refusal) else type(exc).__name__
    return result


def recheck(root, config, original, plan, pair, projection, commit):
    if read(root, '.overseer/config.yaml') != original or check_source(root, config, plan) != projection:
        raise Refusal('mirror_source_or_config_changed')
    if inspect_target(Path(plan['target']), pair) != commit:
        raise Refusal('mirror_target_drift_before_delivery')
    verify_tree(Path(plan['target']), commit, projection['files'])


def deliver(result, transport, revalidate):
    """Delivery state is observed every time; an earlier success flag is never proof."""
    source, dest, commit = result['source'], result['destination'], result['git_head']
    def observe_authority():
        result['authority'] = 'outcome_unknown'
        value = transport.authority(source)
        if value != (source['repo_id'], source['revision']):
            result['authority'] = 'unknown_or_drifted'
            raise Refusal('mirror_authority_unknown_or_drifted')
        result['authority'] = 'observed_matching'
        return value
    def observe_remote():
        value = transport.remote_head(dest)
        result['remote_head'] = value
        return value
    observation = observe_authority()
    revalidate()
    remote = observe_remote()
    if remote not in {dest['expected_head'], commit}:
        raise Refusal('mirror_remote_head_drift')
    if remote != commit:
        # Repeat immediately before the write, including the authoritative source.
        revalidate()
        if observe_authority() != observation or observe_remote() != remote:
            raise Refusal('mirror_remote_changed_before_push')
        result['push'] = 'outcome_unknown'
        try:
            transport.push(Path(result['target']), dest, commit)
        except (Refusal, OSError, subprocess.SubprocessError):
            # A lost response may follow a successful push. Readback resolves it.
            result['push'] = 'interrupted'
        if observe_remote() != commit:
            result['push'] = 'pending_retry'
            raise Refusal('mirror_push_incomplete')
        result['push'] = 'verified'
    else:
        result['push'] = 'already_delivered'
    revalidate()
    if observe_authority() != observation or observe_remote() != commit:
        result['push'] = 'remote_drift_after_push'
        raise Refusal('mirror_remote_changed_before_pr')
    result['pr'] = 'pending_retry'
    result['pr_url'] = transport.ensure_pr(Path(result['target']), dest, source, commit)
    result['pr'] = 'verified'
    result['ok'] = True


class NetworkDelivery:
    """Explicit delivery adapter; tests substitute transport, never real remotes.

    Only public staging JSON refs are supported. Private/authenticated MuseHub and
    production trust are outside R2. No automatic login, trust reset or URL fallback.
    """
    def __init__(self, gh):
        self.gh = physical(gh)
        if not self.gh.is_file() or not os.access(self.gh, os.X_OK):
            raise Refusal('mirror_gh_executable_required')

    def authority(self, source):
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                raise Refusal('mirror_authority_redirect_refused')
        request = urllib.request.Request(source['hub_url'] + '/refs', headers={'Accept': 'application/json'})
        with urllib.request.build_opener(NoRedirect).open(request, timeout=15) as response:
            raw = response.read(2 * 1024 * 1024 + 1)
        if len(raw) > 2 * 1024 * 1024:
            raise Refusal('mirror_authority_response_too_large')
        value = json.loads(raw, object_pairs_hook=unique_json)
        if not isinstance(value, dict) or value.get('domain') != 'code':
            raise Refusal('mirror_authority_domain_mismatch')
        heads = value.get('branch_heads')
        if not isinstance(heads, dict):
            raise Refusal('mirror_authority_refs_invalid')
        return value.get('repo_id'), heads.get(source['branch'])

    def remote_head(self, dest):
        raw = git(Path('/'), 'ls-remote', '--refs', dest['url'], 'refs/heads/' + dest['branch'])
        rows = raw.decode().splitlines()
        if not rows:
            return 'absent'
        fields = rows[0].split('\t')
        if len(rows) != 1 or len(fields) != 2 or fields[1] != 'refs/heads/' + dest['branch'] or not HEX.fullmatch(fields[0]):
            raise Refusal('mirror_remote_response_invalid')
        return rows[0].split('\t')[0]

    def push(self, target, dest, commit):
        git(target, 'push', '--porcelain', dest['url'], commit + ':refs/heads/' + dest['branch'])

    def gh_run(self, target, *args):
        proc = subprocess.run([str(self.gh), *args], cwd=target, env=env(), capture_output=True, timeout=30)
        if proc.returncode:
            raise Refusal('mirror_pr_command_failed')
        return proc.stdout

    def ensure_pr(self, target, dest, source, commit):
        args = ('pr', 'list', '--repo', dest['repository'], '--head', dest['branch'], '--base', dest['base'],
                '--state', 'open', '--json', 'url,headRefOid,isCrossRepository')
        def observe():
            rows = json.loads(self.gh_run(target, *args))
            if len(rows) > 1:
                raise Refusal('mirror_pr_ambiguous')
            if rows and (rows[0]['headRefOid'] != commit or rows[0]['isCrossRepository']):
                raise Refusal('mirror_pr_head_mismatch')
            return rows[0]['url'] if rows else None
        url = observe()
        if not url:
            # A file preserves literal newlines and avoids shell interpretation.
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8') as body:
                body.write(f'Approved Muse snapshot: {source["revision"]}\nSource: {source["hub_url"]}\nGit mirror: {commit}\n')
                body.flush()
                self.gh_run(target, 'pr', 'create', '--repo', dest['repository'], '--head', dest['branch'],
                            '--base', dest['base'], '--title', 'Mirror approved Muse snapshot', '--body-file', body.name)
            url = observe()
        if not isinstance(url, str) or not re.fullmatch(
                re.escape('https://github.com/' + dest['repository'] + '/pull/') + r'[1-9][0-9]*', url):
            raise Refusal('mirror_pr_not_verified')
        return url


def command(root, config, original, args):
    raw = read(root, args.plan_file)
    if digest(raw) != args.expect_plan:
        raise Refusal('mirror_plan_digest_mismatch')
    plan = json.loads(raw, object_pairs_hook=unique_json)
    try:
        validate_plan(plan, root, config)
    except (TypeError, KeyError, AttributeError):
        raise Refusal('mirror_plan_invalid') from None
    transport = NetworkDelivery(args.gh) if args.operation == 'deliver' else None
    return execute(root, config, original, plan, digest(raw), args.operation, transport)
