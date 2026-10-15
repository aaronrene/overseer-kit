// One authorized offline custom-editor persistence/restore cycle.
// Not a Cursor launch, historical-incident reproduction, or acceptance test.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { runRestoreCycle } from './restore-host.mjs';
import { verifyExtensionSource, resolveRestoredWindow } from './extension-host.mjs';
import { verifyRendererSource, captureResumeAdmission } from './renderer-admission.mjs';

const scratch = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'fpr5-ops1-restore-')));
const events = [];
const symbolic = value => JSON.parse(JSON.stringify(value).replaceAll(scratch, '$DISPOSABLE'));
const event = (phase, data = {}) => events.push({ sequence: events.length + 1, phase, ...symbolic(data) });
const result = {
  schema: 1, actionId: 'OVERSEER-FPR5-OPS1-RESTORE-REPRO-1',
  kind: 'Single offline host-API custom-editor restoration experiment; author evidence',
  node: process.version, status: 'preparing', persistenceRestoreCycles: 0,
  historicalCauseEstablished: false, historicalIncidentCleared: false,
  navigationCount: 0, appServerExecuted: false, ipc: 'stubbed',
  fullClientLaunched: false, realProfilesOrAccountsAccessed: false,
  networkUsed: false, installedSourceMutated: false, events,
};
try {
  verifyExtensionSource();
  verifyRendererSource();
  const stateDir = path.join(scratch, 'empty-host-state');
  fs.mkdirSync(stateDir);
  const windows = [], threads = new Map(), ownerByThread = new Map();
  for (const [index, letter] of ['a', 'b'].entries()) {
    const root = path.join(scratch, `repository-${letter}`);
    fs.mkdirSync(root);
    execFileSync('/usr/bin/git', ['-c', 'init.templateDir=', '-c', 'core.hooksPath=/dev/null',
      'init', '--quiet', '--initial-branch=fixture', root], {
      env: { PATH: '/usr/bin:/bin', GIT_CONFIG_NOSYSTEM: '1', GIT_CONFIG_GLOBAL: '/dev/null' },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    const repoId = index === 0 ? '7d521a18-129b-4907-8bbc-2a8c4eac71a1' : '58de70fd-939f-4c48-9f72-092c6d8230b2';
    fs.writeFileSync(path.join(root, 'fixture-repository.json'), JSON.stringify({ repoId, root, synthetic: true }) + '\n');
    const thread = { id: `synthetic-thread-${letter}`, cwd: root, repoId };
    threads.set(thread.id, thread);
    const window = {
      windowId: `synthetic-window-${letter}`, clientId: `synthetic-client-${letter}`,
      workspaceId: `synthetic-workspace-${letter}`,
      membership: { generation: 1, roots: [root], repositoryIds: [repoId] },
      route: `/local/${thread.id}`,
    };
    windows.push(window);
    ownerByThread.set(thread.id, window.clientId);
    event('initial-binding', { ...window, thread, ownership: { source: 'synthetic IPC fixture', role: 'owner', ownerClientId: window.clientId } });
  }
  assert.notEqual(windows[0].route, windows[1].route);
  result.initialWindows = symbolic(windows);
  result.mockThreads = symbolic([...threads.values()]);
  result.status = 'restoring';
  const restored = await runRestoreCycle({ windows, stateDir, eventSink: event });
  result.persistenceRestoreCycles = 1;
  // Live tab API objects include group back-references. Preserve their source
  // snapshots instead of attempting to JSON-serialize those object cycles.
  result.hostRestore = symbolic({ ...restored,
    windows: restored.windows.map(({ tabGroups, ...window }) => window),
  });
  result.status = 'resolving-restored-tabs';
  const bindings = [];
  for (const window of restored.windows) {
    bindings.push(await resolveRestoredWindow({ window, threads, ownerByThread, event }));
  }
  result.restoredBindings = symbolic(bindings);
  result.distinctRoutesConvergedBeforeNavigation = bindings[0].route === bindings[1].route;
  result.naturalWorkspaceTaskMismatch = bindings.some(binding => !binding.workspaceRoots.includes(binding.threadCwd));
  event('pre-navigation-comparison', {
    distinctRoutesConverged: result.distinctRoutesConvergedBeforeNavigation,
    naturalWorkspaceTaskMismatch: result.naturalWorkspaceTaskMismatch,
    routes: bindings.map(binding => binding.route), navigationCount: 0,
  });
  result.status = 'admission';
  const admissions = [];
  for (const binding of bindings) {
    admissions.push(await captureResumeAdmission({
      windowId: binding.windowId, clientId: binding.clientId, root: binding.workspaceRoots[0],
      thread: threads.get(binding.threadId), route: binding.route, event,
      membershipGeneration: 1, probe: 'restored-matching-membership',
    }));
  }
  // One diagnostic input change after the same restore; no route navigation.
  const b = bindings[1], driftRoot = windows[0].membership.roots[0];
  event('injected-membership-drift', {
    windowId: b.windowId, clientId: b.clientId, route: b.route, threadId: b.threadId,
    threadCwd: b.threadCwd, oldMembership: windows[1].membership,
    newMembership: { generation: 2, roots: [driftRoot], repositoryIds: windows[0].membership.repositoryIds },
    origin: 'explicit diagnostic fixture change; not spontaneous convergence', navigationCount: 0,
  });
  admissions.push(await captureResumeAdmission({
    windowId: b.windowId, clientId: b.clientId, root: driftRoot,
    thread: threads.get(b.threadId), route: b.route, event,
    membershipGeneration: 2, probe: 'injected-post-restore-membership-drift',
  }));
  result.admissions = symbolic(admissions);
  result.status = 'captured';
  result.limitations = [
    'Custom-editor surface only; sidebar, OS window recreation/deduplication and real Electron lifecycle not executed.',
    'Per-window workspace identifiers are synthetic host API inputs, not recovered historical window descriptors.',
    'Distinct-route result does not clear the historical incident or identify its route-selection trigger.',
    'Membership drift is deliberately injected after restoration; it is not evidence that restoration created a mismatch.',
    'App-server and IPC are stubbed. Request dispatch does not prove backend acceptance, effective sandbox grants, turn/tool execution or writes.',
    'Current installed bundle hashes do not establish incident-time byte identity.',
  ];
} catch (error) {
  result.failedPhase = result.status;
  result.status = 'blocked';
  result.blocker = { name: error.name, message: error.message, stack: error.stack };
  event('capture-stopped', result.blocker);
  process.exitCode = 1;
} finally {
  fs.rmSync(scratch, { recursive: true, force: false });
  result.disposableStateRemoved = !fs.existsSync(scratch);
  console.log(JSON.stringify(result, null, 2));
}
