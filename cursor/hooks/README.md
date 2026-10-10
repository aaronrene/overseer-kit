> **Historical pre-reset product.** This document describes the pre-reset historical product.
> Its legacy commands are not exposed by the bounded-v1 entrypoint. Do not use it
> as current onboarding. See the [root README](../../README.md) and [current docs index](../../docs/README.md).

# Bounded v1 hooks

`ok init --hooks` or `ok sync --hooks` generates repository-bound sessionStart and
stop hooks. Both read canonical NEXT; neither writes documents or performs
closeout actions. No PATH, OVERSEER_OK, neighboring checkout, or cached-prompt
fallback exists. Hook output is JSON with additional_context/followup_message.
Foreign cwd, copied bound hook/launcher, or conflicting workspace_roots refuses
without a prompt. Only disposable fixture activation is authorized in milestone 1.
