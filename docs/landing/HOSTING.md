# Public site hosting (overseerkit.com)

**Purpose:** Static front door — explain Overseer Kit structure, link suite doors, and document how to
**Open the local console** (Paths 1–3).
**Not a product runtime.** No signup, no chatbot embedding, no session/CSRF mint, no governed-repo
creation, no write APIs, no live `ok app` on this domain.

## Domain map (§LAC.8)

| Host | Content |
| --- | --- |
| `overseerkit.com` (apex) | Static landing ONLY (`docs/landing/`) |
| Optional `docs.overseerkit.com` | Static docs mirror (still not a live `ok app`) |
| Any `app.*` / `console.*` subdomain | **Forbidden** if it pretends to host live Path B/C without a separate Thinking freeze |
| Hosted governance dashboard | Different CLI: `ok hosted-dashboard` — must not be branded as the apex product console |

DNS cutover itself is **Tier 3** (human operator). See pre-public gate §LAC.9 in
`docs/PHASE-LANDING-ACCESS-CLARITY.md`.

## Positioning

Developer-centric door into related projects:

| Door | Why |
| --- | --- |
| **Download Mac console** | Signed Apple Silicon (`.dmg`) from GitHub Release — Path 1; requires Python 3.11+ and `OVERSEER_REPO_ROOT` for consumer repos |
| **GitHub `overseer-kit`** | Clone / `ok init` — Paths 2–3 and secondary quickstart |
| **MuseHub** | Optional deeper substrate (L3) |
| **Knowtation / Scooling / VideoFactory** | Sister products / consumers that *use* the kit for governance while they handle tasks |

Day-to-day runtime UX for tasks stays in those products. This site only explains and routes.

## What to host

Serve the static tree under `docs/landing/` (GitHub Pages, Cloudflare Pages, Netlify, S3+CDN, etc.):

| Path | Role |
| --- | --- |
| `/` or `/index.html` | Main landing — structure diagrams + console access playbook |
| `/scenarios/` | Scenario gallery |
| `/assets/style.css` | Styles (no CDN) |
| `/assets/diagrams/*.svg` | Offline structure flowcharts |

Canonical source stays this repo. Prefer publishing from `main` after merge (Tier 3).

Example GitHub Pages path if publishing the whole `docs/` folder:

`https://<user>.github.io/overseer-kit/landing/`

Map **overseerkit.com** (DNS CNAME / A records) to that host. TLS via the host.

## What this domain is *not*

| Claim | Status |
| --- | --- |
| End-user frontend product / task runner | **No** — Scooling (and peers) own product runtime |
| Live Path B/C console on the apex | **No** — local loopback only (`ok app` / desktop) |
| Website mints `session_credential` / CSRF | **Never** |
| Zero-install “create my project” in the browser | **Not shipped** |
| Hosted write dashboard for merge/deploy | **Rejected** for kit |
| Unsigned installer as primary Download | **Rejected** |
| Windows/Linux signed installers ready | **Unavailable** until a signed Release row ships |
| “No Python required” for desktop Path 1 | **False** — Python 3.11+ still required on the host |

## Primary adopt path (honest)

1. **Preferred (Apple Silicon Mac):** Download the signed `.dmg` from the frozen Release asset on
   the landing hero (GitHub Releases `v0.1.0`), set `OVERSEER_REPO_ROOT`, launch.
2. **Developers:** Clone GitHub + `ok app` (Path 2) or build desktop from source (Path 3).

## License note (already open source)

This repo is **already open source** under **Apache-2.0** (K12). “Make it open source” does not
require a license change. MIT is an optional shorter flavor; switching needs a Thinking freeze
that amends K12 §K12.4. Default recommendation remains **keep Apache** unless you specifically
want MIT branding.
