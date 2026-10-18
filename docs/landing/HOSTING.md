# Public informational site

`overseerkit.com` serves the static files in `docs/landing/` through the existing
Cloudflare Pages project `overseer-kit`. The website explains the Overseer governance
loop and the maintained kit’s explicit manual workflow. It
does not run Overseer, initialize repositories, perform reviews or execute tasks.

## Published routes

| Path | Content |
| --- | --- |
| `/` | Original landing layout with the plan-review, phased-build and completion-review workflow |
| `/docs.html` | Governance workflow, current CLI boundary, installation and repository guides |
| `/scenarios/` | Original persona flows, clearly labelled as governance patterns or examples |
| `/source.html` | Accepted manual source identity, later-candidate boundary and source preparation guide |
| `/assets/style.css` | The original responsive styles, including light and dark themes |
| `/assets/theme.js` | Optional theme preference only |

All four pages work without JavaScript. Theme selection is an enhancement.
The repository's website assets include no analytics script, application backend,
credential prompt or repository-access integration. Hosting can add scripts to the
served HTML: the recorded PR #92 production checks observed one Cloudflare analytics
script on each of the four pages. See the [merge verification record](../validation/PR-92-MERGE.md).
The deployed website therefore must not be described as having no tracking script.
The script's presence does not establish its account-level configuration or data
collection settings; those require authenticated read-only verification.

The original diagrams remain in their original positions and explain
the operating model. Their surrounding copy makes clear that independent humans or
agent sessions perform review judgment and project repositories own domain checks.
The current CLI can run explicitly invoked review and verification commands;
this static website cannot.

The primary action opens `source.html`, distinguishing the accepted manual snapshot
from later development. Historical rc.1 links retain their immutable targets.
No new public release or existing-project installation is authorized.
Git-only setup needs no Muse installation or account.

## Local verification

Open `docs/landing/index.html` directly in a browser. Verify all four pages at
desktop and mobile widths, with JavaScript disabled, and in light and dark
themes. Follow current guide/release links. Compare the DOM structure, stylesheet,
theme script and image bytes with the approved original presentation baseline;
only factual text and link destinations should differ.

## Existing publication controls

The project publishes `docs/landing/` from GitHub. Normal pull-request activity
creates the preview; an authorized merge to `main` triggers production deployment.
This website does not merge or deploy. The kit's PR-landing command requires
separate explicit authorization. Do not manually create or retry a Pages
deployment or change project settings as part of documentation publication.

Before accepting a preview, verify its exact candidate commit, pages and links.
After an authorized merge, authenticated read-only Cloudflare requests must confirm
successful production, branch `main`, the resulting commit, canonical deployment,
active `overseerkit.com` ownership and project controls. Compare controls with a
recorded baseline before claiming that they are unchanged. Include any analytics
injection settings visible through the authorized read-only connection. Read-only
HTTP checks of the four public pages supplement that authenticated verification;
they do not establish account ownership or project configuration. If authenticated
access is unavailable, record those checks as unverified rather than inferring
success from public content or the GitHub deployment check. Do not change settings
to reconcile the documentation.
