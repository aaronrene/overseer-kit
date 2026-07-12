# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x | Yes |

Security fixes apply to the current kit release line tracked in `VERSION` at the repository root.

## Reporting a vulnerability

If you discover a security issue in Overseer Kit (CLI, adapters, vendored templates, or
landing-site validator):

1. **Preferred:** Open a [GitHub private security advisory](https://github.com/aaronrene/overseer-kit/security/advisories/new) on this repository.
2. **Alternate:** Email **security@overseer-kit.dev** with a description, reproduction steps, and impact assessment.

Please do **not** open a public issue for undisclosed vulnerabilities.

### What to include

- Affected command, config key, or file path
- Steps to reproduce (fixture repo layout if relevant)
- Whether the issue requires local repo access, network access, or Tier-3 operator action
- Any suggested fix (optional)

### Response expectations

- **Acknowledgment:** within 72 hours of a valid report
- **Critical issues** (remote code execution, secret exfiltration, fail-open on governance gates):
  best-effort patch on the next kit release line
- **Lower severity:** scheduled with the normal phase queue

## Out of scope

- Consumer domain packs under `docs/consumers/` (report to the owning project)
- Third-party MuseHub runtime or Muse CLI (report to MuseHub maintainers)
- Misconfiguration in consumer `.overseer/config.yaml` when the kit behaved per frozen spec

## Safe disclosure practices

- Never commit API keys, tokens, or private keys into test fixtures or landing pages.
- `OVERSEER_REVIEW_API_KEY` and similar secrets belong in environment variables only — never in config YAML.
