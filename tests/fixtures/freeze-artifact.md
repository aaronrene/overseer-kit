# Test freeze artifact

```yaml
phase: K5b-test
outputs:
  - id: test-output
    path: docs/TEST-FREEZE.md
    frozen: true
frozen_inputs:
  - id: parent-spec
    path: docs/OVERSEER-KIT-SPEC.md
```

This artifact includes a seven-tier test matrix reference and file+line citation discipline.
