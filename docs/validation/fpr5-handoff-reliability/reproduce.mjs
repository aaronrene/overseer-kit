// Offline source-boundary reproduction. No client, app-server, account or provider.
// Run: node docs/validation/fpr5-handoff-reliability/reproduce.mjs
// Seeded restored state is a hypothesis input, not recovered incident state.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';

const sourceMapBytes = fs.readFileSync(new URL('./source-map.json', import.meta.url));
const sourceMap = JSON.parse(sourceMapBytes);
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const used = ['C1', 'E1', 'E2', 'E3', 'E8', 'R1', 'R2'];
for (const id of used) {
  const entry = sourceMap.excerpts[id];
  assert.equal(sha(entry.text), entry.sha256, `changed excerpt ${id}`);
}
// Only these inspected, saved routines run. No entire extension bundle is loaded.
const code = id => sourceMap.excerpts[id].text;
const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'fpr5-ops1-source-repro-'));
try {
  const rootA = path.join(scratch, 'project-a');
  const rootB = path.join(scratch, 'project-b');
  fs.mkdirSync(rootA); fs.mkdirSync(rootB);
  const uri = { scheme: 'openai-codex', authority: 'route', path: '/local/synthetic-thread-a', query: '' };
  const windows = [];
  for (const root of [rootA, rootB]) {
    const opened = [], ownerRequests = [], panels = new Map();
    class CustomTab { constructor(uri) { this.uri = uri; } }
    class TextTab {}
    const context = vm.createContext({
      Ie: {
        window: { tabGroups: { all: [{ tabs: [{ input: new CustomTab(uri), isPreview: false }] }] } },
        workspace: { workspaceFolders: [{ uri: { fsPath: root } }] },
        TabInputCustom: CustomTab, TabInputText: TextTab,
        Uri: { joinPath: (...parts) => parts.join('/') },
        commands: { executeCommand: (...args) => { opened.push(args); } },
      },
      ph: 'openai-codex', oPe: 'route', t: { customEditorViewType: 'chatgpt.conversationEditor' },
      Uke: value => value ?? 'Synthetic conversation',
      eI: async (_client, timeout) => timeout,
      uf: value => value?.workspace != null, Mu: value => value?.folderUri != null,
      wn: values => values.filter(Boolean),
    }, { codeGeneration: { strings: false, wasm: false } });
    vm.runInContext(`${code('E2')} ${code('R1')} ${code('R2')}`, context, { timeout: 1000 });
    const restore = vm.runInContext(`({${code('E1')}})`, context, { timeout: 1000 });
    await restore.ensureRestoredConversationTabsResolved();
    assert.equal(opened.length, 1);
    const resolver = vm.runInContext(`({${code('E3')}})`, context, { timeout: 1000 });
    Object.assign(resolver, {
      conversationSummaryProvider: { getConversationSummary: async () => ({ summary: {} }) },
      extensionUri: 'synthetic-extension', editorPanels: panels,
      registerOnDidDisposeForWebviewPanel() {}, initializeWebview: async () => {},
      previewLoader: { fetchConversationPreviews: async () => new Map() }, isPanelAlive: () => true,
    });
    const panel = { webview: {}, onDidDispose() {} };
    await resolver.resolveCustomEditor({ uri: opened[0][1] }, panel, {});
    context.inputs = { requestedCwd: root, responseCwd: null, threadCwd: rootA, fallbackCwd: root };
    const cwd = vm.runInContext('i$(inputs)', context, { timeout: 1000 });
    context.resolvedCwd = cwd; context.windowRoots = [root];
    const roots = Array.from(vm.runInContext('y6t(resolvedCwd,windowRoots,"synthetic-projectless")', context, { timeout: 1000 }));
    const discovery = vm.runInContext(`({${code('E8')}})`, context, { timeout: 1000 });
    Object.assign(discovery, {
      ownerDiscoveryTimeoutMs: 1000,
      ipcClient: { sendRequest: async (method, params, options) => {
        ownerRequests.push(JSON.parse(JSON.stringify({ method, params, options })));
        return { resultType: 'success', handledByClientId: 'synthetic-owner-a' };
      } },
    });
    const owner = await discovery.findThreadOwner({ hostId: 'local', conversationId: 'synthetic-thread-a' });
    const symbolic = value => value.replace(scratch, '$DISPOSABLE');
    windows.push({ windowRoot: symbolic(root), seededRestoredUri: uri,
      route: panels.get(panel).initialRoute, resolvedCwd: symbolic(cwd),
      resumeRootCandidates: roots.map(symbolic), ownerRequests, mockedOwnerResponse: owner,
      workspaceTaskMismatch: root !== cwd });
    // Positive control: the same cwd arbitration retains an explicitly requested descendant.
    context.inputs.requestedCwd = path.join(rootA, 'nested');
    assert.equal(vm.runInContext('i$(inputs)', context, { timeout: 1000 }), context.inputs.requestedCwd);
  }
  assert.equal(windows[0].route, '/local/synthetic-thread-a');
  assert.equal(windows[1].route, windows[0].route);
  assert.equal(windows[1].resolvedCwd, windows[0].resolvedCwd);
  assert.equal(windows[0].workspaceTaskMismatch, false);
  assert.equal(windows[1].workspaceTaskMismatch, true);
  assert.deepEqual(windows[0].ownerRequests, windows[1].ownerRequests);
  const policyContext = vm.createContext({});
  const policyMethod = code('C1').slice(code('C1').indexOf('getRestoreWindowsSetting(){'));
  const policy = vm.runInContext(`({${policyMethod}})`, policyContext, { timeout: 1000 });
  policy.configurationService = { getValue: () => ({ restoreWindows: 'none' }) };
  policy.lifecycleMainService = { wasRestarted: false };
  const ordinary = policy.getRestoreWindowsSetting();
  policy.lifecycleMainService.wasRestarted = true;
  const appRestartFlag = policy.getRestoreWindowsSetting();
  assert.equal(ordinary, 'none'); assert.equal(appRestartFlag, 'all');
  console.log(JSON.stringify({
    kind: 'New isolated source-function reproduction; not a client incident reproduction or acceptance test',
    node: process.version, sourceMapSha256: sha(sourceMapBytes),
    executedExcerpts: used, windows,
    cursorPolicy: { configured: 'none', ordinary, appRestartFlag,
      incidentFlagValue: 'unknown; application lifecycle flag is not inferred from OS restart' },
    demonstrated: 'Seeded shared restored URI is reopened in both windows; cwd arbitration retains project A; owner discovery omits workspace identity.',
    notDemonstrated: ['How the incident selected the shared URI', 'Whether incident views were sidebar or custom editor',
      'Full renderer resume or effective sandbox grants', 'Actual owner arbitration, tool execution or cross-repository writes',
      'Cursor lifecycle events or restart qualification'],
    sourceChanged: false, fullClientsLaunched: false, networkUsed: false,
    scratchPolicy: 'Only two new empty directories; removed by finally',
  }, null, 2));
} finally {
  fs.rmSync(scratch, { recursive: true, force: false });
}
