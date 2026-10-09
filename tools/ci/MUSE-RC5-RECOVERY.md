# Muse rc5 recovery distribution

This is an Overseer recovery of verified locally installed **0.2.1rc5** package
bytes, not an upstream release, recovered original sdist, or rebuild of upstream
build sources. The original archive remains unavailable. The wheel keeps Muse's
version and uses build tag `1overseerrecovery`; `OVERSEER_RECOVERY.json` inside its
dist-info records that distinction. No Muse Python source or package data changes.

`muse-rc5-artifact.json` pins the recovery source ZIP, wheel, full input manifest,
and Python source digest. `muse-rc5-source-files.json` covers all 388 original
payload files, including metadata and license, verified against installed RECORD
hashes and the R3 recovered wheel. The original sdist digest in the contract is
historical pip provenance, **not** an accepted artifact or proof of its contents.

The source ZIP is a recovery payload archive, not an installable upstream sdist:
it contains original package/data/dist-info bytes, not upstream tests, build config
or a full upstream source repository. Generated install metadata, launchers,
bytecode and RECORD are excluded. The wheel changes only WHEEL packaging metadata,
adds recovery provenance, and regenerates RECORD. ZIP entries are sorted, stored
uncompressed, timestamped 1980-01-01, and fixed to regular-file mode 0644. Thus
rebuilding uses the Python standard library without a downloaded build backend,
clock, host path, source mtime, permission or compression-version dependency.

From this source checkout, use an empty/new output destination:

```sh
python tools/ci/muse_artifact.py rebuild \
  --source-archive /absolute/path/muse-0.2.1rc5-overseer-recovery1-source.zip \
  --output-dir /absolute/path/new-output
python tools/ci/muse_artifact.py verify \
  --wheel /absolute/path/new-output/muse-0.2.1rc5-1overseerrecovery-py3-none-any.whl
```

Bootstrap recovery can instead use `--installed-root /absolute/site-packages`
from the original verified rc5 installation. This reads files without importing
Muse and refuses unexpected package data/code. It requires the original metadata;
an installation of the recovery wheel is not that bootstrap input. Preserve the
source ZIP to rebuild independently of the original environment. Every output
digest must match the committed contract before any artifact is written.

Install only the verified wheel into a **separate** Python 3.14 venv using
`pip install --constraint tools/ci/requirements-muse-rc5.txt /absolute/wheel.whl`,
then `pip check`. The kit keeps its own conventional `.venv`, installed from
`requirements-v1-dev.txt`. Run `tools/ci/supported_v1.py` with the kit Python and
explicit `--muse-python /absolute/muse-venv/bin/python`. It verifies rc5's version
and exact source digest before running the full suite. Git-only CI never needs
this archive, tool, dependency or Muse installation.

Runtime dependencies are constrained to the versions tested locally. Dependency
wheels are fetched from PyPI; their hashes, availability on other platforms and
the surrounding Python/toolchain are not a fully locked offline supply chain.
There is no claim of reproducible third-party native binaries or upstream rc5
release authenticity from local RECORD validation alone.

CI now requires `MUSE_RC5_RECOVERY_WHEEL_URL` to name an HTTPS copy of the exact
recovery wheel. The old `MUSE_RC5_URL` contract is superseded, not silently reused.
The verifier checks the exact wheel filename/digest before pip runs; the runner
also checks the installed Python source. Missing URL, wrong bytes or another Muse
version fail. There is no fallback to the moving installer or PyPI's `muse` name.
Artifacts remain in local recovery evidence; they are not committed or published.
Hosting them, configuring repository variables, and running hosted CI require
separate authorization. Muse-first product publication remains a later gate.
