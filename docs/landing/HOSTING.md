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
| **GitHub `overseer-kit`** | Clone / `ok init`, rendered docs, releases — Paths 2–3 and secondary quickstart |
| **Optional Muse deepen** | Same CLI; optional L3 substrate — do **not** link a broken public MuseHub TLS origin from this site |

Day-to-day product UX stays in the operator’s own apps. This site only explains Overseer Kit.

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

### Preview the landing locally (not the Path B console)

From the kit checkout:

```bash
open docs/landing/index.html
# or, if you prefer an http:// origin:
cd docs/landing && python3 -m http.server 8080
# then open http://127.0.0.1:8080/
```

That is the **marketing site**. The governance UI is a different process:

| Local URL | Command | What it is |
| --- | --- | --- |
| `http://127.0.0.1:8765/` | `ok app --open` (from a governed repo) | Track Q Path B console |
| `http://127.0.0.1:8766/` | `ok hosted-dashboard --open` | Read-only remote glance (not Path B) |

### Operator cutover checklist (Tier 3) — make `overseerkit.com` live

1. Merge the landing branch to `main` (Muse → GitHub mirror PR) — Tier 3 merge.
2. Enable static hosting of `docs/landing/` as site root (recommended: Cloudflare Pages publish
   directory = `docs/landing`; or GitHub Pages from `/docs` then serve `/landing/`).
3. At your DNS registrar for **overseerkit.com**: attach apex + optional `www` to that host
   (Cloudflare “Custom domains” on the Pages project is usually simplest).
4. Wait for TLS; open `https://overseerkit.com/` and confirm hero + OK favicon + Download CTA still
   target the signed Mac `.dmg`. Loopback links (`127.0.0.1:8765`) on the page only work for
   visitors who already started `ok app` on their own machine.
5. Do **not** create `app.` / `console.` subdomains that host live Path B.

## What this domain is *not*

| Claim | Status |
| --- | --- |
| End-user frontend product / task runner | **No** — your apps own product runtime |
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
