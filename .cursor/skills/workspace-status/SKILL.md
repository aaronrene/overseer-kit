# Workspace status

Use the repository-bound launcher with an explicit root. Run `ok workspace status`,
`ok workspace check-next --lane product` and `ok workspace doctor` for the
configured constellation. Only explicitly declared absolute member roots are read.
Every member owns its identity, settings, authority, runtime and canonical NEXT.

Report required and optional member failures separately; status `--strict-all`
makes optional failures fatal. Doctor reports naming/identity/manifest conflicts.
Exit 35 indicates a member or relay refusal. Relay pins bind the whole canonical
NEXT digest. Never discover neighboring repositories or scrape HANDOVER prompts.
This read-only skill cannot mutate members or invent a cross-repository action.
