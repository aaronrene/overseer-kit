# Public informational site

`overseerkit.com` serves the static files in `docs/landing/` through the existing
Cloudflare Pages project `overseer-kit`. The website explains the bounded-v1 local
CLI. It does not run Overseer, initialize repositories or execute tasks.

## Published routes

| Path | Content |
| --- | --- |
| `/` | Trusted NEXT, daily flow, operating choices and prerelease installation |
| `/docs.html` | Current guides and the seven public commands |
| `/scenarios/` | Clearly labelled examples of actual bounded-v1 behavior |
| `/assets/style.css` | Local responsive styles, including light and dark themes |
| `/assets/theme.js` | Optional theme preference only |

All three pages work without JavaScript. Theme selection is an enhancement;
no application backend, tracking script, credential prompt or repository access
is involved. Retained historical diagrams are marked as historical and are not
current product guidance. The current pages do not embed them.

The primary release link selects **v1.0.0-rc.1**, a prerelease, not stable and not
Latest. Installation and rollback links select its immutable companion guide.
Git-only setup needs no Muse installation or account.

## Local verification

Open `docs/landing/index.html` directly in a browser. From the kit source root:

```sh
.venv/bin/python -B -m tools.landing.validate .
```

Verify all three pages at desktop and mobile widths, with JavaScript disabled,
and in light and dark themes. Follow current guide/release links. Check HTML
structure, keyboard navigation, readable contrast and local asset paths.

## Existing publication controls

The project publishes `docs/landing/` from GitHub. Normal pull-request activity
creates the preview; an authorized merge to `main` triggers production deployment.
Overseer itself does not merge or deploy. Do not manually create or retry a Pages
deployment or change project settings as part of documentation publication.

Before accepting a preview, verify its exact candidate commit, pages and links.
After an authorized merge, authenticated read-only Cloudflare requests must confirm
successful production, branch `main`, the resulting commit, canonical deployment,
active `overseerkit.com` ownership and unchanged project controls. Read-only HTTP
checks of the three public routes supplement that authenticated verification.
