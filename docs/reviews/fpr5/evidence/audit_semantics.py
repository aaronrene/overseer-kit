"""Attach source-backed reviewer assessments to every preserved historical failure."""
import ast
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path('/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014')
OUT = Path('/private/tmp/overseer-fpr5-review.jTlE9P/evidence')
BASE = ROOT / 'docs/validation/fpr4'
audit = json.loads((BASE / 'disposition-audit.json').read_text())
collection = json.loads((BASE / 'disposition-closeout-collection.json').read_text())['cases']

def source(selector):
    path, name = selector.split('::', 1)
    name = name.split('[')[0].split('::')[-1]
    text = (ROOT / path).read_text()
    tree = ast.parse(text)
    node = next(n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    return {'path': path, 'line': node.lineno, 'end_line': node.end_lineno,
            'file_sha256': hashlib.sha256(text.encode()).hexdigest(),
            'body': ast.get_source_segment(text, node)}

app_gaps = {
 'tests/e2e/test_q1_app_e2e.py::test_full_operator_flow':
  'Selected successors cover authentication, bound identity, canonical NEXT, status/documents and governance dry-run. They do not execute successful review dry-run, ledger show/verify or honesty-status through the local HTTP adapter, although those engines have independent CLI coverage.',
 'tests/integration/test_q1_app_integration.py::test_gates_slice_matches_status':
  'None of the mapped successors requests /api/gates or asserts equality with /api/status governance_gates. Selected CLI status tests do not execute handle_gates or HTTP routing/envelopes.',
 'tests/integration/test_q1_app_integration.py::test_review_freeze_dry_run':
  'The mapped local HTTP review request exercises only an outside-path refusal. No selected local HTTP test executes a valid dry-run with a fake provider and verifies the resulting verdict; shared CLI review tests bypass this HTTP body-to-argv adapter.',
 'tests/e2e/test_q4b_ui_e2e.py::test_overview_structure_status_roadmap_actions':
  'Static/source-install guidance, diagram/document reads and status are covered. The original valid review dry-run action has no selected local HTTP successor; the preserved fake-provider route remains a maintained capability.',
 'tests/integration/test_q1_app_integration.py::test_status_exit_code_matches_cli':
  'Selected successors assert successful repeated bound HTTP status and separately assert CLI status, but no selected case compares the same repository HTTP status exit_code with the actual CLI exit status. This is a narrower coverage limitation than a demonstrated behavior defect.',
}

def assessment(row):
    node = row['original_pytest_node']; path = row['original_file']
    if node in app_gaps:
        return {'status': 'partial_maintained_http_outcome_coverage', 'assessment': app_gaps[node],
                'finding': 'EVIDENCE-HTTP-OUTCOMES', 'requirement': ['docs/decisions/FULL-PRODUCT-RESTORATION-PLAN.md:520', 'docs/decisions/FULL-PRODUCT-RESTORATION-PLAN.md:550']}
    if row['original_selected_now']:
        return {'status': 'retained_original_pass_verified', 'assessment': 'The original failed node itself was rerun and passed in raw JUnit on the fixed production boundary, with its original test source byte-identical. Additional mapped successors are supplemental.'}
    if 'test_atomic_writes' in path:
        note = 'Confined atomic failure preserves old bytes/removes temporary files; bound engine CAS/context refusal and migration partial-write/config-last resume cover the maintained outcome. Legacy implicit initialization is not required.'
    elif any(s in path for s in ('test_migrate_idempotency', '/test_sync.py', 'test_k7_footprint_check')):
        note = 'Current sync rejects generic force takeover and explicit --preserve-modified retains owner bytes/origins; bound footprint timing and preservation checks pass. This is not evidence for default legacy migration of custom content colliding with a distributed asset: the migration fixture uses non-colliding custom paths.'
    elif 'test_cost_awareness' in path:
        note = 'Actual bound status/route and retained pure cost/routing tests cover current configured policy resolution; the old injected CLI fixture is not reused. The mapped real-entrypoint case primarily verifies successful routing and field presence, rather than reproducing every old profile-value assertion.'
    elif 'test_lt_e2e' in path:
        note = 'Bound ledger append/verify/show and honesty status, restored status fields, and retained warn-mode ISR behavior cover the maintained engines; legacy HANDOVER prompt authority remains excluded.'
    elif 'workspace' in path:
        note = 'Current canonical NEXT plus whole-file relay pins replace archived HANDOVER selection. Real bound workspace members, required/optional handling, strict-all, board-name refusal, duplicate identities, no ambient manifest and nondefault lane ownership are exercised across the selected lane/workspace cases; output shape and default filename changes are explicit.'
    elif 'config-muse-only' in node:
        note = 'Pinned native initialization/product status and local review/hygiene execute without Git initialization. Full installed footprint and explicit native/mirror selection replace historical shell-adapter/CLI injection.'
    elif 'hosted_dashboard' in path:
        note = 'Actual hosted CLI SIGINT/startup/static read is exercised without upstream access; other selected hosted originals and fixture upstream tests cover read-only projections, allowlists and auth. Live provider/transport behavior remains unclaimed.'
    elif 'q2_ok_cli' in path:
        note = 'Actual ok/overseer shims emit equal JSON, preserve literal hostile arguments, fail copied-runtime fallback and meet the stated latency bound. The per-process deprecation warning is explicitly retired by the accepted quiet compatibility contract.'
    elif 'release_desktop' in path:
        note = 'Manual-only workflows, read-only permissions, no publishing steps/credentials, clean-workflow scan and deterministic source artifacts replace absent signed-release workflows. Native signing/publication are unresolved scope cells, not inferred passing outcomes.'
        if 'secret_scanner_flags_pem' in node:
            note += ' The selected replacement checks clean-workflow scanning but does not repeat the positive PEM-detection assertion; that assertion precedes the historical missing-workflow failure, and scanner source is retained. No new positive-scanner execution is claimed.'
    elif 'q3_desktop' in path:
        note = 'Actual bound desktop child launch, exact root/UUID/runtime health, canonical NEXT readback, five launch/stop cycles, fresh ephemeral secrets, repository nonpersistence and source bundle validation cover current source-install desktop behavior. Native GUI interaction/signing is outside this local evidence.'
    elif any(s in path for s in ('q1_app', 'q4b_ui', 'lac_')):
        note = 'Bound loopback auth/CSRF/origin/path refusal, status/doc reads, canonical NEXT, static UI, concurrent status/SVG requests, size/latency bounds, shutdown and no persisted secrets cover this mapped current app outcome. Source-install copy and explicit repository targeting replace ambient root and unsigned DMG promises.'
        if 'health_additive_no_full_repo_walk' in node:
            note += ' The old 200-call/0.25-second path-only health threshold is explicitly changed to validated identity/runtime health; selected bound health startup is under two seconds, not a pass of that historical benchmark.'
        if 'governance_sync_dry_run_idempotent' in node:
            note += ' Repository nonmutation is checked; the exact repeated HTTP result-equality assertion is not repeated by these mapped successors.'
    else:
        note = 'Current-contract successor source and raw passing evidence were inspected; the preserved historical failure remains failed, not relabelled green.'
    return {'status': 'mapped_current_contract_scope_assessed', 'assessment': note}

rows = []
for row in audit['historical_failures']:
    rows.append({'historical_node': row['historical_node'], 'category': row['historical_category'],
                 'author_contract_reason': row['contract_reason'], 'reviewer': assessment(row),
                 'original_source': source(row['original_pytest_node']),
                 'successor_sources': [{'selector': s, **source(s)} for s in row['successor_nodes']],
                 'raw_evidence': row['final_original_evidence'] + row['final_successor_evidence']})

replacement_reviews = {
 'tests/v1/test_commands.py::test_unsupported_commands_cannot_run':
  'Accepted changed scope: restoring the full registry contradicts the old unconditional unsupported-command assertions. Actual help/registry/effect-refusal checks supplement the selected successful command/body tests. No legacy_main execution is reintroduced.',
 'tests/v1/test_adoption.py::test_fresh_standalone_git_install_without_muse':
  'Accepted fixture dependency correction: full product declares exact PyYAML/cryptography/cffi/pycparser pins. Successor provisions only those installed distributions into a fresh conventional venv, verifies actual crypto use and absent Muse/pip/pytest, and runs both source/bound launchers. Same-interpreter copying is not a Python 3.11 compatibility claim.',
 'tests/muse/test_handoffs.py::test_native_linked_worktree_own_branch_and_checkout_identity':
  'Accepted truthful dirty-state contract: successor retains own UUID/branch/source identity, primary-byte preservation and independent NEXT freshness; it asserts the only portable delta is version.lock, verifies changed launcher digest and preserved origins, and reports dirty=True.',
 'tests/muse/test_mirror.py::test_add_change_delete_and_no_content_source_commit':
  'Accepted fixture correction: successor explicitly stages all portable hidden files, calls the unchanged original delta/retry assertions, and independently compares native snapshot IDs plus Git trees for the intended no-content commit. No source product behavior is weakened.',
 'tests/unit/test_k7_footprint.py::test_rendered_deploy_script_safety_invariants':
  'Accepted explicit-effects replacement: direct git-export/automatic push/bridge sentinel are superseded. Rendered-wrapper test verifies physical root, exact literal argv, PATH sanitization, missing-launcher refusal and exit propagation; native target/projection/delivery/current-source tests cover the maintained mirror invariants.',
 'tests/unit/test_skills_footprint.py::test_footprint_includes_orchestrator_rule':
  'Accepted semantic guidance replacement: obsolete rule number/HANDOVER placeholder tokens are not requirements. Installed-rule successor checks canonical NEXT, identity/authority, CAS, paired summaries, explicit effects/review gates, independent-vs-author evidence and both host skill footprints.',
 'tests/fpr1/test_dispatch.py::test_git_core_imports_no_muse_or_provider_engine':
  'Accepted definition-vs-execution correction: two isolated-bootstrap cases cover local and API settings, absent/forbidden native Muse, provider-call guards, network/process audit guards, complete status identity and unchanged bytes/modes/mtimes. Pure protocols/dataclass definitions are allowed; actual provider engine execution remains barred. Same production/dependencies were independently reconciled; raw combined failure remains visible.',
}
explicit = []
for row in audit['additional_changed_contract_cases']:
    explicit.append({'original_node': row['node'], 'assessment': replacement_reviews[row['node']],
                     'status': 'replacement_maintains_stated_requirement_with_explicit_limits',
                     'original_source': source(row['node']),
                     'successor_sources': [{'selector': s, **source(s)} for s in row['successors']]})

selected_sources = {}
for case in collection:
    selector = case['nodeid'].split('[', 1)[0]
    if selector not in selected_sources:
        try:
            selected_sources[selector] = source(selector)
        except (StopIteration, SyntaxError):
            pass
queries = ['/api/gates', '/api/review/freeze', '/api/ledger/show', '/api/ledger/verify', '/api/honesty-status',
           'handle_gates(', 'handle_ledger_verify(', 'handle_honesty_status(']
occurrences = {q: [{'selector': s, 'path': d['path'], 'line': d['line'], 'body': d['body']}
                   for s, d in selected_sources.items() if q in d['body']] for q in queries}

families = []
for row in audit['files']:
    families.append({'path': row['path'], 'author_disposition': row['disposition'],
                     'historical_rows_reviewed': [r['historical_node'] for r in rows if r['original_source']['path'] == row['path']],
                     'original_selectors': row['original_selectors'], 'successor_nodes': row['successor_nodes'],
                     'review_scope': 'source preservation and raw mapped case identities verified; per-failure semantic assessment is recorded separately'})
migration_limitation = {
 'status': 'coverage_limitation_corresponding_to_root_reproduced_product_finding',
 'scope': 'Subreview independently inspected fixture/classification source; root owns the runtime reproduction and final product finding.',
 'requirement': 'docs/decisions/FULL-PRODUCT-RESTORATION-PLAN.md:253',
 'evidence': ['tests/fpr1/test_migration.py:21', 'tests/fpr1/test_migration.py:63', 'tests/fpr1/test_migration.py:227',
              'tests/fpr3/test_engines.py:58', 'tests/fpr4/test_disposition_contracts.py:257'],
 'assessment': 'Legacy lossless fixture uses custom filenames outside shipped targets. Preserved collision coverage sets origin=preserved explicitly; changed owner rule coverage runs sync --preserve-modified. Those cases do not exercise default migrate applying an unrecorded custom file at a shipped rule path. Historical init/migration families mapped to these successors therefore do not close that requirement.'}

result = {'scope': 'Independent evidence semantics subreview; inputs read only; no separate final verdict or product repair.',
          'historical_rows': rows, 'explicit_replacements': explicit, 'original_file_families': families,
          'selected_function_endpoint_occurrences': occurrences,
          'migration_preservation_limitation': migration_limitation,
          'summary': {'historical_rows': len(rows), 'explicit_replacements': len(explicit),
                      'assessments': dict(collections.Counter(r['reviewer']['status'] for r in rows)),
                      'not_claimed': 'Equivalence of every historical assertion, a green historical suite, a second all-green combined execution, release readiness, or runtime verification of every HTTP outcome.'}}
(OUT / 'independent-semantic-replacement-map.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result['summary'], indent=2))
