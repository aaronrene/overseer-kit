# Overseer Muse rc5 recovery — CI dependency only

These are recovered Muse 0.2.1rc5 package bytes, not an upstream release,
original upstream sdist, or Overseer product release. The original upstream
archive remains unavailable. Package source/data and embedded license are
preserved. The wheel uses build tag 1overseerrecovery and contains explicit
OVERSEER_RECOVERY.json provenance. The source ZIP is a recovery payload;
it is not a complete upstream source repository or installable upstream sdist.

Rebuild/verification recipe and input manifest:
https://github.com/aaronrene/overseer-kit/tree/86d7a78f2b29440eebcbf97dc1afda9fdaa1f4e7/tools/ci

SHA-256:

6b596288fd61f1d0373ead76eff90f82b14291984bff2dbecf9e51cf0694eb4d  muse-0.2.1rc5-1overseerrecovery-py3-none-any.whl

28f5fefacf5860b600edbb83e3cdd35485b983a900ab229a2a1ea673776ae3f0  muse-0.2.1rc5-overseer-recovery1-source.zip

Retain this branch and immutable commit while CI depends on these files.
Do not overwrite artifacts or use the branch name as a mutable CI download pin.
