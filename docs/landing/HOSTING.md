# Public informational site

`overseerkit.com` serves the static files in `docs/landing/` through the existing
Cloudflare Pages project `overseer-kit`. The website explains the Overseer governance
loop and the bounded-v1 local CLI that preserves continuity between its steps. It
does not run Overseer, initialize repositories, perform reviews or execute tasks.

## Published routes

| Path | Content |
| --- | --- |
| `/` | Original landing layout with the plan-review, phased-build and completion-review workflow |
| `/docs.html` | Governance workflow, current CLI boundary, installation and repository guides |
| `/scenarios/` | Original persona flows, clearly labelled as governance patterns or examples |
| `/assets/style.css` | The original responsive styles, including light and dark themes |
| `/assets/theme.js` | Optional theme preference only |

All three pages work without JavaScript. Theme selection is an enhancement;
no application backend, tracking script, credential prompt or repository access
is involved. The original diagrams remain in their original positions and explain
the operating model. Their surrounding copy makes clear that independent humans or
agent sessions perform review judgment and project repositories own domain checks;
the current CLI does not automate either role.

The primary release link selects **v1.0.0-rc.1**, a prerelease, not stable and not
Latest. Installation and rollback links select its immutable companion guide.
Git-only setup needs no Muse installation or account.

## Local verification

Open `docs/landing/index.html` directly in a browser. Verify all three pages at
desktop and mobile widths, with JavaScript disabled, and in light and dark
themes. Follow current guide/release links. Compare the DOM structure, stylesheet,
theme script and image bytes with the approved original presentation baseline;
only factual text and link destinations should differ.

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
