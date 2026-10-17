# Security Policy

## Supported versions

The published `v1.0.0-rc.1` prerelease is the historical bounded CLI.
The `1.0.0.dev1` manual source release and this later integration are separate
identities; see the [acceptance boundary](docs/reviews/FPR-5-MANUAL-ACCEPTANCE.md)
and [publication record](docs/validation/PUBLICATION-PREPARATION.md).
Neither source version is a stable-release or signed-installer claim.

## Design boundary

The manual workflow protects against stale state and ordinary operator mistakes on a trusted
local host. It validates physical repository binding, UUID, branch, declared lane
and model label, action metadata, prompt digest, expected prior digest, runtime pin,
and selected Git or Muse revision freshness. It confines managed reads/writes, refuses symlinks and hardlinks,
and replaces NEXT atomically.

It is not a sandbox or a security boundary against the operating-system
administrator, root, or another malicious process running as the same user. It does
not verify the actual AI model or enforce a vendor’s execution permissions.
Local handoff commands stay offline. Provider calls, configured verification
scripts and PR landing are explicit commands requiring their own authorization.
Explicitly invoked
`mirror deliver` contacts MuseHub/GitHub, pushes the verified mirror commit and
creates or verifies its pull request; it never merges that request.

## Reporting a vulnerability

Open a private GitHub security advisory at
<https://github.com/aaronrene/overseer-kit/security/advisories/new>. Do not open a
public issue for an undisclosed vulnerability.

Include the affected command/file, supported version, reproduction steps using a
disposable Git repository when possible, impact, and whether local repository or
same-user access is required. Never include real tokens, private keys, or consumer
data in a report or fixture.

Third-party tools and archived modules are outside this source contract.
See README for the maintained command families. A vulnerability that makes a maintained command escape its
repository boundary, print a foreign/refused prompt, accept stale context, or expose
data should be reported.
