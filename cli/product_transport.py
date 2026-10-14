"""Explicit optional post-land transport with checks around intentional transitions."""
import subprocess
from cli import v1
from cli.v1_io import Refusal


def post_land_git(b, argv):
    from cli.main import ValidatedContext
    if not b.args.post_land_sync or not b.args.allow_network or not b.args.authorized:
        raise Refusal('post_land_sync_not_authorized')
    if argv[0] != 'git' or argv[1] not in {'fetch', 'status', 'rev-parse', 'checkout', 'pull'}:
        raise Refusal('post_land_sync_command_refused')
    b.recheck()
    prior = b.context
    try:
        # A dirty tree is never switched, even if a legacy setting waived it.
        if argv[1] in {'checkout', 'pull'} and v1.revision(prior.root, prior.config, dirty=True).dirty:
            return subprocess.CompletedProcess(argv, 1, '', 'dirty tree; no local transition')
        output = v1.git(prior.root, *argv[1:])
        if argv[1] in {'checkout', 'pull'}:
            current = ValidatedContext.capture(prior.root, b.args)
            if current.original != prior.original or current.observed['branch'] != prior.config['vcs']['git']['main_branch']:
                raise Refusal('post_land_sync_binding_changed')
            b.context = current
        b.recheck()
        return subprocess.CompletedProcess(argv, 0, output, '')
    except Refusal as exc:
        return subprocess.CompletedProcess(argv, 1, '', str(exc))
