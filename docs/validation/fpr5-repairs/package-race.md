# Archive test scheduling failure

The integrated retained group failed
`test_provisioned_runtime_and_actual_packaged_entrypoints` inside
`source_package.build` → `verify`, before runtime provisioning. The preserved
[log](integrated/repaired-integrated-retained.log),
[JUnit](integrated/repaired-integrated-retained.xml) and
[exact command](integrated/repaired-integrated-retained.json) retain that failure.

Read-only inspection of its failed archive found exactly two mismatches between
`SOURCE-MANIFEST.json` and archived bytes: the concurrently written foundation
FPR1 log was 69 bytes in the manifest and 70 in the archive; the foundation V1 log
was 48 and 49 bytes respectively. Both SHA-256 values also differ; modes match.
[The diagnosis](package-race-diagnosis.json) records the exact rows, archive path,
archive SHA-256, runtime, command and traceback. This confirms changing evidence
inputs caused the archive guard to refuse. It does not change the failed result.

To reproduce the diagnosis without rerunning tests, open the recorded failed
archive with Python `tarfile`, load `SOURCE-MANIFEST.json`, and compare each regular
member's actual size, SHA-256 and mode with its manifest entry. This reads the
original failed bytes and needs no extraction, network or execution of the bundle.

The scheduling correction is to defer both archive-producing cases until all
other evidence writers finish: the existing FPR3 deterministic archive case and
this FPR5 packaged-entrypoint case. Run only those affected cases afterward with
the existing driver and a new evidence basename. Keep the original failure and
subsequent results separate. No product or test change, weaker archive guard,
runtime change or independent certification follows from this diagnosis.
