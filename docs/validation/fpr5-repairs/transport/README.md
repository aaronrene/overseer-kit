# FPR5-R1/R2 bounded repair author evidence

These are new repair-author results, not an independent adjudication. The
original FPR-5 FINDINGS verdict and `docs/reviews/fpr5` evidence remain unchanged.
No external provider, credential, real consumer, live merge or delivery was used.

R1 changes the actual default urllib transport to use a private opener that
refuses every redirect. A 3xx remains an unsuccessful upstream response; it
cannot initiate a second request or forward authorization, including to another
allowlisted host, another port, a downgrade, the same host or a relative target.
The requirement tests retain urllib's real response/redirect processing and
inject only synthetic HTTP responses. Socket creation is forbidden by the probe.

R2 enforces the configured GitHub remote at the shared `gh_run` boundary. Number,
matching HTTPS PR URL and valid branch selectors remain supported. Option-shaped,
foreign and malformed selectors refuse before the explicit fake executable is
called. Every invocation has an explicit configured `--repo` as well as pinned
`GH_REPO`/`GH_HOST`; returned PR number and URL must agree with that repository
and any requested number. Branches resolve once to a PR number used by checks and
merge. A changed configured remote refuses. Authorization and dry-run merge
guards remain enforced; configured post-land sync still requires separate consent.
The retained PR polling engine and historical tests were not edited.

`tests/fpr3/test_engines.py` has one fixture correction: its fake `gh pr view`
now returns the requested number and bound URL, alongside `state: OPEN`.
The old response omitted identity, which a correct target-binding guard cannot
accept. This changes no requirement assertion and does not rewrite old run logs.
The 393 inventoried historical test/support files remain unchanged.

| Run | Result | Runtime SHA-256 |
| --- | --- | --- |
| `before` | 89 failed / 5 passed, 108.47 s | `bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec` |
| `after` | 94 passed, 114.42 s | `64a075b0eea2ca53beb8d18935c0a65630e1466388c00e1465293c8763b6de8d` |
| `affected` | 110 passed / 1 failed, 63.64 s | `0e0260d272063e4572cabe8bda19f3bafd7d23500936ab1a879024cbdc8143a5` |
| `affected-successor` | 1 passed, 4.23 s | `0e0260d272063e4572cabe8bda19f3bafd7d23500936ab1a879024cbdc8143a5` |
| `branch-before` | 1 failed, 3.78 s | `0e0260d272063e4572cabe8bda19f3bafd7d23500936ab1a879024cbdc8143a5` |
| `branch-dot-before` | 1 failed, 3.63 s | `0e0260d272063e4572cabe8bda19f3bafd7d23500936ab1a879024cbdc8143a5` |
| `branch-at-before` | 1 failed, 3.08 s | `0e0260d272063e4572cabe8bda19f3bafd7d23500936ab1a879024cbdc8143a5` |
| `branch-after` | 3 passed, 10.90 s | `cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774` |

Each runtime was stable across its run. Both use HEAD
`4c62c17cff6c606a5e1ddf565e12353973b3bcad`; `after` is the recorded uncommitted
repair candidate, not that commit's original source. The same 94-case regression
file ran before and after: 60 redirect cases, one redirect response-mapping case,
and 33 PR selection/identity/authorization/sync cases. The complete repaired source
and final integrated validation are recorded separately at repair closeout.

The affected batch covers hosted unit/security/integration/e2e/integrity/stress/
performance, retained PR polling, all post-land-sync families and FPR-3 engine/
surface integration. Its one failure is the preserved historical
`test_cli_preview_sigint_exit_zero_no_vcs_mutation`: its fabricated unbound
repository/config omits current binding and authorization, so the current CLI
refuses with exit 2. Selecting the whole historical file was an author selection
error. The existing FPR-4 [disposition](../../fpr4/disposition-audit.json) already
maps that case to
`test_actual_client_cli_sigint_shutdown_is_read_only[hosted-dashboard]`, which
passed in the separate successor run. The 110-pass/one-failure batch remains a
failed execution; the successor is not merged into a synthetic all-green result.
Neither historical source nor historical failures were changed. The affected
runs used scoped loopback permission because the sandbox denies local binding;
upstreams stayed synthetic, and CLI lifecycle requests accessed local static
content only. The source remained stable across each run; the later runtime
includes the independently authored foundation correction, while transport source
hashes stayed unchanged.

Author checks subsequently caught three valid Git branch forms that the initial
repair candidate rejected: a non-ASCII decimal digit name (`٧`), an interior
component ending with a dot (`feature./topic`), and `@`. The three `branch-*-before`
records preserve those candidate failures. The final repair uses the existing
bound, read-only local Git runner for `check-ref-format --branch`, refusing
option-shaped values, NUL and revision expressions before validation. The resolved
identity check distinguishes ASCII PR numbers from Unicode branch names. All
three additional cases passed after this correction; the full regression file now
contains **97 cases**. These are author-candidate corrections, not new independent
review findings. The final frozen integrated matrix supplies the complete result
on the corrected source rather than combining these separate executions.

Final owned production SHA-256 values are
`525fac38f7d2813a442ba74be075e1ea76fa69158b7555acaa1c43ec2c0c3bba`
for `tools/hosted_dashboard/http_client.py` and
`9727c6f0e40749e93060423c9c1b370bb23bcf621d713512af8c418b7e03b3ce`
for `cli/product_service.py`. `tools/close_ritual/pr_land.py` remains byte-identical
to the original source. Final integrated commit identity and acceptance blockers
are maintained by the repair closeout, not inferred from these intermediate runs.

Each run directory contains raw log/XML and `command.json` with exact argv,
environment overrides, physical fixture root, Python version, full HEAD/branch,
runtime before/after, owned source/test hashes and artifact hashes. Use the
conventional venv and a new evidence label to reproduce without overwriting:

```sh
.venv/bin/python -I -B docs/validation/fpr5-repairs/transport/run.py NEW-LABEL
```

The helper creates a fresh fixture parent under `/private/tmp`. Additional pytest
selectors may follow the label. It never reuses the historical review fixtures.
These local Python 3.14 results do not establish Python 3.11, native host/version,
platform/distribution acceptance or the separately authorized new pilot. One final
independent adjudication and a separate owner release decision remain necessary.
