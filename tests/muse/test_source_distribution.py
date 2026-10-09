"""The native snapshot and controlled mirror must retain supported CI dotfiles."""
import json
import subprocess

from tests.muse.test_handoffs import init
from tests.v1.conftest import KIT, command


def test_native_source_and_mirror_keep_ci_dotfiles(muse_root, muse_python, muse, tmp_path):
    root = muse_root
    init(root, muse_python)
    paths = ['.github/workflows/supported-v1.yml', '.museignore', '.gitignore',
             'tools/ci/supported_v1.py', 'templates/ROADMAP.template.md']
    for relative in paths:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((KIT / relative).read_bytes())
    tool = root / 'explicit-tool'
    tool.write_bytes(b'no shebang; mode is explicit\n')
    tool.chmod(0o755)
    muse(root, 'code', 'add', '.')
    # rc5's recursive staging omits new dot-directories; explicitly stage CI.
    muse(root, 'code', 'add', '.github/workflows/supported-v1.yml')
    muse(root, 'commit', '--no-verify', '-m', 'source including CI dotfiles', '--json')
    head = muse(root, 'rev-parse', 'HEAD').stdout.strip()
    state = json.loads(command('-C', root, 'status', '--json').stdout)
    plan = {'schema': 1, 'source': {'repo_id': state['source_id'], 'branch': 'main',
            'revision': head, 'hub_url': 'https://staging.musehub.ai/fixture/ci'},
            'destination': {'url': 'https://github.com/fixture/ci.git',
                'repository': 'fixture/ci', 'branch': 'muse-mirror', 'base': 'main',
                'expected_head': 'absent'}, 'target': str((tmp_path / 'ci-mirror.git').resolve()),
            'expected_target': 'absent', 'executables': ['explicit-tool']}
    from cli.v1_io import digest
    raw = json.dumps(plan).encode()
    file = root / '.overseer/local/ci-plan.json'
    file.parent.mkdir(exist_ok=True)
    file.write_bytes(raw)
    for operation in ('prepare', 'verify'):
        result = command('-C', root, 'mirror', operation, '--plan-file',
                         '.overseer/local/ci-plan.json', '--expect-plan', digest(raw))
        assert result.returncode == 0, result.stderr + result.stdout
    def git(*args):
        return subprocess.check_output(['/usr/bin/git', '--git-dir', plan['target'], *args])
    projected = git('ls-tree', '-r', '--name-only', 'refs/heads/muse-mirror').decode().splitlines()
    assert set(paths) <= set(projected)
    for relative in paths:
        assert git('show', 'refs/heads/muse-mirror:' + relative) == (root / relative).read_bytes()
    assert git('ls-tree', 'refs/heads/muse-mirror', 'explicit-tool').startswith(b'100755 ')
    assert not any(p.startswith(('.overseer/', '.cursor/')) or p == 'docs/NEXT.md' for p in projected)
    assert not (root / '.muse/hooks').exists()
    assert not (root / '.cursor').exists()
