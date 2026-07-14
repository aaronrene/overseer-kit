# Public site hosting (overseerkit.com)

**Purpose:** Static front door — explain Overseer Kit layers/patterns and link into the suite.
**Not a product runtime.** No signup, no chatbot embedding, no governed-repo creation, no write APIs.

## Positioning

Developer-centric door into related projects:

| Door | Why |
| --- | --- |
| **GitHub `overseer-kit`** | Install and use the governance CLI (`ok`) |
| **MuseHub** | Optional deeper substrate (L3) |
| **Knowtation** | Sister knowledge/vault product |
| **Scooling** (and other consumers) | Product runtimes that *use* the kit for governance while they handle tasks |

Day-to-day runtime UX for tasks stays in those products. This site only explains and routes.

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

## What this domain is *not*

| Claim | Status |
| --- | --- |
| End-user frontend product / task runner | **No** — Scooling (and peers) own product runtime |
| Zero-install “create my project” in the browser | **Not shipped** |
| Hosted write dashboard for merge/deploy | **Rejected** for kit |
| Signed desktop installers as primary adopt path | Optional later; developers clone GitHub |

## License note (Apache-2.0 — keep unless a freeze changes it)

K12 froze **Apache-2.0** (patent grant + OSI). Prefer keeping Apache over switching to MIT unless
a later Thinking phase reopens license choice — see ROADMAP exploration / operator decision.
MIT is simpler to read; Apache adds an express patent license/termination useful for multi-org
tooling. Do not silently rewrite `LICENSE` without amending the K12 contract.
