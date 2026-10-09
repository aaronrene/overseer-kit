# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 1.x | Yes |
| 0.x and historical pre-reset commands | No |

Security fixes apply to the latest published 1.x release. A version written in the
source tree is not published until the matching GitHub Release exists.

## Design boundary

Bounded v1 protects against stale state and ordinary operator mistakes on a trusted
local host. It validates physical repository binding, UUID, branch, declared lane
and model label, action metadata, prompt digest, expected prior digest, runtime pin,
and Git freshness. It confines managed reads/writes, refuses symlinks and hardlinks,
and replaces NEXT atomically.

It is not a sandbox or a security boundary against the operating-system
administrator, root, or another malicious process running as the same user. It does
not verify the actual AI model, judge prompt quality, execute prompts, contact the
network, update itself, push, merge, release, or deploy.

## Reporting a vulnerability

Open a private GitHub security advisory at
<https://github.com/aaronrene/overseer-kit/security/advisories/new>. Do not open a
public issue for an undisclosed vulnerability.

Include the affected command/file, supported version, reproduction steps using a
disposable Git repository when possible, impact, and whether local repository or
same-user access is required. Never include real tokens, private keys, or consumer
data in a report or fixture.

Historical modules outside the bounded-v1 entrypoint and third-party tools are not
supported surfaces. A vulnerability that makes a supported v1 command escape its
repository boundary, print a foreign/refused prompt, accept stale context, or expose
data should be reported.
