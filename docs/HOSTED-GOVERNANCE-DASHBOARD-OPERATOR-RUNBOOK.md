# Hosted Governance Dashboard — Operator Runbook

Read-only remote glance of ROADMAP / HANDOVER / document-derived gates via GitHub
(and optional MuseHub) **read** APIs. Authoritative workflow remains the local
`ok` CLI / Track Q. This surface never mutates git, muse, GitHub, or MuseHub.

Frozen contract: `docs/PHASE-HOSTED-GOVERNANCE-DASHBOARD.md`.

## What this is / is not

| Is | Is not |
| --- | --- |
| Org/repo governance glance for operators without a checkout | Track Q (`ok app`) port or rewrite |
| Preview via `ok hosted-dashboard` (default `127.0.0.1:8766`) | CD / deploy console / live product health probe |
| Bearer viewer auth + separate upstream read token | Write-capable GitHub/MuseHub automation |

## Credentials (required)

| Env | Role |
| --- | --- |
| `OVERSEER_HOSTED_DASHBOARD_VIEWER_TOKEN` | Viewer Bearer (≥ 128 bits). If unset in preview, an ephemeral token is printed **once** to stderr at startup. |
| `OVERSEER_HOSTED_DASHBOARD_TOKEN` | Upstream **read** credential for GitHub Contents/meta (and optional checks). Synonym: `OVERSEER_HOSTED_DASHBOARD_GITHUB_TOKEN`. |
| `OVERSEER_HOSTED_DASHBOARD_SCOPES` | Optional comma-separated introspected scope list. If any write-class token is present, process start refuses with `write_scope_refused` (exit `2`). |

**Never** commit tokens into the repo, living docs, or `version.lock`.

### Upstream scope policy

Use a **read-only** credential (fine-grained: Contents read + Metadata read; or classic
with the narrowest read access your org allows).

**Refuse** credentials that advertise write-class scopes such as `contents:write`,
`administration`, `workflows` / `workflow`, or full classic `repo` when introspected.
If the host cannot report scopes, you still must provision read-only credentials —
the code path only issues upstream `GET`/`HEAD`.

## Config block

Optional (default inert) in `.overseer/config.yaml`:

```yaml
hosted_dashboard:
  enabled: false
  allow_non_loopback: false
  cors_origins: []
  org_allowlist: []          # "owner/repo" or org-only "owner"
  sources:
    github_contents: true    # required baseline (K7)
    github_meta: true        # required baseline (K7)
    github_checks_advisory: false
    musehub_read: false
  # Optional Muse deepen (finite hosts only — no wildcards):
  # musehub_hosts: [musehub.example.com]
  # musehub_base_url: https://musehub.example.com
```

Empty `org_allowlist` → org summary returns zero repos (fail closed).

## Local preview

```bash
export OVERSEER_HOSTED_DASHBOARD_TOKEN=<github-read-token>
# optional: export OVERSEER_HOSTED_DASHBOARD_VIEWER_TOKEN=<long-random>
./cli/ok hosted-dashboard --port 8766 --bind 127.0.0.1 --config .overseer/config.yaml
```

Paste the viewer token into the UI bootstrap once per browser load (JS memory only —
no `localStorage` / `sessionStorage`).

| Flag | Default | Notes |
| --- | --- | --- |
| `--port` | `8766` | Occupied → exit `2` (no silent hop). Distinct from Track Q `8765`. |
| `--bind` | `127.0.0.1` | Non-loopback requires `allow_non_loopback: true` plus auth; TLS required for non-loopback hosted deploys. |
| `--config` | cwd `.overseer/config.yaml` if present | Path-confined |
| `--open` | off | Optional browser open |

Exit codes: `0` clean shutdown · `1` usage · `2` config/bind/scope/listen failure.

## Upstream hosts (allowlist)

Default: `api.github.com`, `raw.githubusercontent.com`.

Optional Muse deepen may add **exactly** the hostnames listed in `musehub_hosts`
(finite; no `*`). Literal IPs and link-local/metadata addresses are always refused
(`upstream_host_refused` / HTTP `403`).

## CORS

`cors_origins` is an allowlist. Missing `Origin` (same-origin / non-browser) is allowed.
Any non-allowlisted explicit `Origin` → HTTP `403`.

## K7 note

No core hosted-dashboard feature may be MuseHub-only. `github_contents` + `github_meta`
remain the baseline for `git-only` orgs. `musehub_read` is optional deepen only.

## Hard stops

- No Track Q rewrite / no teaching `ok app` to bind non-loopback for hosting
- No kit-owned durable multi-tenant store of consumer governance docs
- No CD/deploy/production product URL probes
- No Tier-3 merge authorization from this surface
