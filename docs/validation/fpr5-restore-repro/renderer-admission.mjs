// Offline installed-source resume admission adapter. Importing this file does not
// run the experiment. No Electron/app-server/backend or whole bundle is loaded.
import fs from 'node:fs';
import vm from 'node:vm';
import { createHash } from 'node:crypto';

const sourceFile = new URL('./renderer-admission-source.json', import.meta.url);
const sha256 = value => createHash('sha256').update(value).digest('hex');
const clone = value => value === undefined ? undefined : JSON.parse(JSON.stringify(value));

export function verifyRendererSource() {
  const manifest = JSON.parse(fs.readFileSync(sourceFile, 'utf8'));
  const body = fs.readFileSync(manifest.source.path);
  if (sha256(body) !== manifest.source.sha256) throw new Error('renderer bundle digest changed');
  for (const [name, excerpt] of Object.entries(manifest.excerpts)) {
    const bytes = body.subarray(excerpt.byte_start, excerpt.byte_end_exclusive);
    if (sha256(bytes) !== excerpt.sha256 || bytes.toString('utf8') !== excerpt.text) {
      throw new Error(`renderer excerpt changed: ${name}`);
    }
  }
  return { source: clone(manifest.source), excerpts: Object.keys(manifest.excerpts).length };
}

function createSourceContext() {
  const manifest = JSON.parse(fs.readFileSync(sourceFile, 'utf8'));
  const context = vm.createContext({});
  const declarations = Object.entries(manifest.excerpts)
    .filter(([, value]) => value.kind === 'function' || value.kind === 'constant')
    .map(([name, value]) => value.kind === 'constant' ? `var ${value.text};` : value.text)
    .join('\n');
  // Compilation/evaluation defines exact declarations only; module initializers,
  // imports, app bootstrap, network transports and real storage are not evaluated.
  new vm.Script(declarations, { filename: 'installed-renderer-admission-excerpts.js' })
    .runInContext(context);
  const method = (name, property = name) => new vm.Script(
    `({${manifest.excerpts[name].text}})[${JSON.stringify(property)}]`,
    { filename: `installed-renderer-${name}.js` },
  ).runInContext(context);
  const ownershipCallback = new vm.Script(
    `(function(t){return ${manifest.excerpts.canAcquireOwnership.text}})`,
    { filename: 'installed-renderer-ownership-callback.js' },
  ).runInContext(context);
  return { context, method, ownershipCallback };
}

export async function captureResumeAdmission({
  windowId, clientId, root, thread, route, event = () => {},
  membershipGeneration = 1, probe = 'restored-matched',
}) {
  verifyRendererSource();
  if (!windowId || !clientId || !root?.startsWith('/') || !thread?.id || !thread?.cwd?.startsWith('/')) {
    throw new Error('synthetic window, client, absolute workspace root and thread binding required');
  }
  if (typeof route !== 'string' || !route.endsWith(`/${thread.id}`)) {
    throw new Error('caller must supply the thread selected by the actual restored route');
  }
  const { context, method, ownershipCallback } = createSourceContext();
  const identity = { windowId, clientId, hostId: 'local', membershipGeneration, probe };
  const emit = (phase, data) => event(phase, clone({ ...identity, ...data }));
  const conversations = new Map();
  const roles = new Map();
  const writableRoots = new Map([[thread.id, clone(thread.writableRoots ?? [])]]);
  const tokenBudgetThreadIds = new Set();
  let current = true;
  let request = null;
  let permissions = null;
  let preparedStart = null;
  let preparationWorkspaceRoots = null;
  let cleanup;
  const mockThread = {
    id: thread.id, cwd: thread.cwd, repoId: thread.repoId,
    sessionId: `synthetic-session-${thread.id}`,
    name: '', path: null, createdAt: 1, updatedAt: 2,
    recencyAt: 2, historyMode: 'legacy', status: { type: 'idle' },
    source: 'vscode', parentThreadId: null, threadSource: 'user',
    modelProvider: '', turns: [], gitInfo: null,
  };
  const summary = {
    conversationId: thread.id, hostId: 'local', cwd: thread.cwd,
    createdAt: 1000, updatedAt: 2000, recencyAt: 2000,
    title: '', source: 'vscode', parentThreadId: null,
    threadSource: 'user', modelProvider: '', workspaceKind: 'project',
  };
  const settings = {
    personality: null, defaultFeatureOverrides: null, instructionOverrides: null,
    includeProseDetailLevelInstructions: false, automaticTitleCheckpoints: false,
    writingBlocks: false, presentationOutlines: false,
  };
  emit('renderer-resume-fixture', {
    route, workspaceMembership: [root], thread: mockThread, summary, settings,
    writableRoots: writableRoots.get(thread.id),
    tailHydration: false, projectlessAssignments: [], appServerVersion: null,
    permissionsInput: null, hostWindowActivity: { visibilityState: 'visible', canAcquireThreadStream: true },
    perProbeRendererState: 'fresh synthetic conversation and stream-role storage for this admission probe',
  });
  const logger = Object.fromEntries(['info', 'warning', 'debug', 'error'].map(level => [
    level, (message, data) => emit('renderer-log', { level, message, data }),
  ]));
  const requestClient = {
    hostId: 'local',
    getAppServerVersion: () => null,
    async sendRequest(name, params, options) {
      emit('app-server-request', { method: name, params, options });
      if (name === 'thread/read' && params.threadId === thread.id && params.includeTurns === false) {
        return { thread: clone(mockThread) };
      }
      if (name === 'thread/resume' && params.threadId === thread.id) {
        request = clone(params);
        emit('resume-admission-boundary', {
          route, workspaceMembership: [root], authoritativeThreadCwd: mockThread.cwd,
          resolvedTaskCwd: params.cwd, streamRole: roles.get(thread.id) ?? null,
          request, derivedPermissions: permissions,
          workspaceTaskMismatch: params.cwd !== root,
          effectivePermissions: 'not-observed: app-server stub stops at request boundary',
        });
        // Deliberate harness stop at the authorized boundary, using the actual
        // cancellation callback. No invented resume response/permission grant.
        current = false;
        return null;
      }
      throw new Error(`unprovided app-server fixture dependency: ${name}`);
    },
  };
  const getConversation = id => conversations.get(id);
  const updateConversationState = (id, update) => {
    const conversation = conversations.get(id);
    if (!conversation) throw new Error(`missing synthetic conversation state: ${id}`);
    update(conversation);
  };
  const threadStore = {
    params: { hostId: 'local', requestClient },
    threadReadStates: new Map(), backgroundThreadLookups: new Map(),
    updateConversationState,
  };
  const readThread = method('readThread').bind(threadStore);
  const workspace = {
    hostId: 'local', conversationIds: new Set(), workspaceRootHints: new Map(),
    outputDirectoryHints: new Map(), removedConversationIds: new Set(),
    hasFetchedConversationIds: false, getConversation,
    // These are empty synthetic persisted state containers, not replacement
    // classification rules. The real load/classification methods run below.
    loadConversationIds: async () => new Set(),
    loadThreadPathHints: async () => new Map(),
  };
  workspace.load = method('workspaceLoad', 'load').bind(workspace);
  for (const name of ['getThreadWorkspaceKind', 'getThreadWorkspaceBrowserRoot', 'getThreadProjectlessOutputDirectory']) {
    workspace[name] = method(name).bind(workspace);
  }
  const manager = {
    logger, getConversation, updateConversationState,
    getHostId: () => 'local',
    getWindowActivity: () => ({ visibilityState: 'visible', canAcquireThreadStream: true, routePath: route, windowId, clientId }),
    getStreamRole: id => roles.get(id),
    setConversationStreamRole(id, role) {
      if (role == null) roles.delete(id); else roles.set(id, clone(role));
      emit('renderer-stream-role', { conversationId: id, role });
    },
    ensureRecentConversationId: id => emit('renderer-recent-conversation', { conversationId: id }),
    getThreadSummaries: () => [clone(summary)],
    getThreadHasUnreadTurn: () => false,
    setConversation: value => conversations.set(value.id, value),
    useTailHydration: () => false,
    readThread,
    getThreadWorkspaceState: () => null,
    getThreadWritableRoots: async id => clone(writableRoots.get(id) ?? []),
    readShellEnvironmentPolicy: async (cwd, config) => {
      emit('host-shell-environment-policy-read', { cwd, config, syntheticValue: null });
      return null;
    },
    sendRequest: requestClient.sendRequest.bind(requestClient),
  };
  const product = context.M2t({
    restricted: false, isBrowserRuntime: false, usesDesktopMcp: false,
    allowMemoryPromptOverrides: false,
    readCatalogEntry: async () => null,
    readSettings: async (model, cwd, includeDeveloperInstructions) => {
      emit('host-settings-read', { model, cwd, includeDeveloperInstructions, settings });
      return clone(settings);
    },
    fetchProxyConfig: async () => null,
    readCodexConfig: async cwd => {
      emit('host-config-read', { cwd, syntheticValue: {} });
      return {};
    },
    isTokenBudgetThread: id => tokenBudgetThreadIds.has(id),
  }, requestClient, logger, {}, undefined);
  const actualPrepare = product.prepare;
  product.prepare = async input => {
    permissions = clone(input.permissions);
    preparationWorkspaceRoots = clone(input.workspaceRoots);
    emit('renderer-product-prepare-input', {
      authoritativeThreadCwd: input.thread?.cwd,
      conversationCwd: input.conversation?.cwd,
      workspaceRoots: input.workspaceRoots, permissions: input.permissions,
    });
    const result = await actualPrepare(input);
    preparedStart = clone(result.start);
    emit('renderer-product-prepare-output', {
      start: result.start, preserveServerPermissions: result.preserveServerPermissions,
    });
    return result;
  };
  const result = await context._6t({
    manager, workspace, product,
    params: {
      conversationId: thread.id, model: 'synthetic-offline-model',
      workspaceRoots: [root], serviceTier: null,
    },
    historyPolicy: {},
    canAcquireOwnership: ownershipCallback.call(manager, 'view'),
    isCurrentResumeAttempt: () => current,
    setHydrationCleanup: value => { cleanup = value; },
    schedule: () => { throw new Error('unexpected retry scheduling before captured admission'); },
  });
  cleanup?.();
  if (request == null) throw new Error(`resume boundary not reached: ${JSON.stringify(result)}`);
  return {
    ...identity, route, threadId: thread.id, threadRepoId: thread.repoId,
    workspaceMembership: [root], authoritativeThreadCwd: thread.cwd,
    requestedCwd: root,
    requestedCwdMeaning: 'caller-selected window workspace root, not an explicit _6t cwd parameter',
    initialConversationCwd: summary.cwd, resolvedCwd: request.cwd,
    preparationWorkspaceRoots, derivedPermissions: permissions, preparedStart,
    request, streamRole: clone(roles.get(thread.id) ?? null),
    boundary: 'client outgoing thread/resume request captured at stub app-server',
    resumeRequestReached: true, backendResumeExecuted: false, turnAdmitted: null,
    turnAdmission: 'not exercised; stopped at resume request',
    effectivePermissions: 'NOT OBSERVED: no app-server response or sandbox grant',
    workspaceTaskMismatch: request.cwd !== root,
    result: clone(result),
    stopReason: 'harness canceled after request capture, before backend response/history hydration',
    limitations: [
      'Each admission probe has fresh renderer conversation/role stores; no completed resume or owner transition is simulated.',
      'Actual canAcquireOwnership callback runs with synthetic visible-window canAcquireThreadStream=true host activity.',
      'Empty projectless assignments and missing thread workspace transition state are synthetic persisted-state fixtures.',
      'Settings APIs return explicitly recorded disabled optional feature flags and no proxy or extra config.',
      'Derived permissions and request fields are client outputs, not effective backend or sandbox grants.',
      'No turn admission, tool dispatch, history hydration or backend resume is executed.',
    ],
  };
}
