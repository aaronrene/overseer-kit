"""Track O / O3 Stage 3 kit upgrade ceremony (`muse-only` → `muse+git-mirror`).

Composes existing init/sync/status + K7 bridge invariants per frozen
``docs/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md`` (§O2.3–§O2.7).
"""

from tools.upgrade_regime.ceremony import (
    BRIDGE_DESTINATIONS,
    StartState,
    UpgradeReport,
    build_upgraded_config_dict,
    classify_start_state,
    docs_preserved,
    evaluate_bridge_gates,
    is_silent_regime_only_patch,
    required_vcs_complete,
    run_upgrade_regime,
)

__all__ = [
    "BRIDGE_DESTINATIONS",
    "StartState",
    "UpgradeReport",
    "build_upgraded_config_dict",
    "classify_start_state",
    "docs_preserved",
    "evaluate_bridge_gates",
    "is_silent_regime_only_patch",
    "required_vcs_complete",
    "run_upgrade_regime",
]
