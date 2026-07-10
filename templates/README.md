# Templates — token-parameterized governance doc skeletons

Copied into consumer repos by `overseer init` / `overseer sync` (K4) with substitution from
`.overseer/config.yaml`.

| Template | Becomes (typical) |
| --- | --- |
| `OVERSEER-HANDOVER.template.md` | `{{docs.handover_path}}` |
| `ROADMAP.template.md` | `{{docs.roadmap_path}}` |
| `STANDING-DECISIONS.template.md` | section in `{{docs.standing_decisions_path}}` or standalone |
| `CROSS-REPO-COORDINATION.template.md` | `{{docs.coordination_path}}` when configured |

## Token substitution

Placeholders use `{{dotted.key}}` form. Allowed keys are frozen in `tokens.yaml` and enforced by
`adapters.templating` — unknown tokens fail closed.

```python
from pathlib import Path
from adapters.config import load_config
from adapters.templating import render_template

config = load_config(Path(".overseer/config.yaml"))
text = render_template(Path("templates/OVERSEER-HANDOVER.template.md"), config)
```

Kit ships **format and skeletons**, not repo-specific Standing Decision contents.
