# Public site hosting (overseerkit.com)

**Purpose:** Point a custom domain at the static K12 landing already in this repo.
**Not a product runtime.** No signup, no governed-repo creation, no write APIs.

## What to host

Serve the static tree under `docs/landing/` (GitHub Pages, Cloudflare Pages, Netlify, S3+CDN, etc.):

| Path | Role |
| --- | --- |
| `/` or `/index.html` | Main landing — L0→L3 explanation |
| `/scenarios/` | Scenario gallery |
| `/assets/style.css` | Styles (no CDN) |

Canonical source stays this repo. Prefer publishing from `main` after merge (Tier 3).

Example GitHub Pages path if publishing the whole `docs/` folder:

`https://<user>.github.io/overseer-kit/landing/`

Map **overseerkit.com** (DNS CNAME / A records) to that host. TLS via the host.

## What visitors can do today

1. Read what Overseer Kit is (layers, personas, funnel).
2. Open GitHub and follow the git-only quickstart **or** use a product that wraps kit CLI.
3. After a project is installed, day-to-day non-dev work is **Path A** (paste the handover prompt into any chatbot) — not a magic button on this site.

## What this domain is *not* (yet)

| Claim | Status |
| --- | --- |
| Zero-install “create my project” in the browser | **Not shipped** — Track O Stage 1 UX is product-owned (e.g. Scooling), not kit core |
| Hosted write dashboard for merge/deploy | **Rejected** for kit — `ok hosted-dashboard` is read-only glance operators run themselves |
| Download signed desktop installers from the marketing site | Only after a GitHub Release publishes signed assets (operator Tier 3); link to Releases when that exists |
| Cursor or Muse required to understand the product | **No** — landing is static HTML |

## Recommendation

Use **overseerkit.com** as the public front door: brand, layer story, scenarios, GitHub CTA.
Keep the kit itself installable from the repo. Promote product shells separately when they ship
signup without asking users to touch a terminal.
