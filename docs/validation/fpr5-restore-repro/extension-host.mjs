// Isolated custom-editor host API adapter. Only pinned routines are evaluated.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';

const source = JSON.parse(fs.readFileSync(new URL('./extension-source-map.json', import.meta.url)));
const sha = value => createHash('sha256').update(value).digest('hex');
export function verifyExtensionSource() {
  for (const entry of Object.values(source.sources)) {
    assert.equal(sha(fs.readFileSync(entry.path)), entry.sha256);
  }
  for (const entry of Object.values(source.excerpts)) {
    const bytes = fs.readFileSync(source.sources[entry.file].path);
    assert.equal(bytes.subarray(entry.byte_start, entry.byte_end_exclusive).toString(), entry.text);
    assert.equal(sha(entry.text), entry.sha256);
  }
}
const code = id => source.excerpts[id].text;

export async function resolveRestoredWindow({ window, threads, ownerByThread, event }) {
  const identity = { windowId: window.windowId, clientId: window.clientId,
    workspaceId: window.workspaceId, membership: window.membership };
  const emit = (phase, data) => event(phase, { ...identity, ...data });
  const opened = [], panels = new Map(), pending = [];
  class CustomTab { constructor(uri) { this.uri = uri; } }
  class TextTab {}
  const hostTabs = window.tabGroups.map(group => ({ tabs: group.tabs.map(tab => ({
    ...tab, input: new CustomTab(tab.uri ?? tab.input?.uri),
  })) }));
  const context = vm.createContext({
    ...source.constants,
    t: { customEditorViewType: 'chatgpt.conversationEditor' },
    mn: (_key, fallback) => fallback, // Host configuration: no WSL.
    document: { querySelector: () => null },
    window: { location: { href: 'https://offline.invalid/' } }, URL,
    e: init => init, // U1 bundle initializer is defined, not executed.
  }, { codeGeneration: { strings: false, wasm: false } });
  const vscode = {
    window: { tabGroups: { all: hostTabs } },
    workspace: { workspaceFolders: window.membership.roots.map(root => ({ uri: { fsPath: root, scheme: 'file' } })) },
    TabInputCustom: CustomTab, TabInputText: TextTab,
    Uri: { joinPath: (...parts) => parts.join('/') },
    commands: { executeCommand: (command, uri, viewType, options) => {
      assert.equal(command, 'vscode.openWith');
      assert.equal(viewType, 'chatgpt.conversationEditor');
      opened.push({ command, uri, viewType, options });
      emit('extension-open-restored-tab', { uri, command, options, origin: 'host-restored-custom-editor' });
      const panel = { webview: {}, onDidDispose() {} };
      const promise = resolver.resolveCustomEditor({ uri }, panel, {}).then(() => {
        const route = panels.get(panel).initialRoute;
        const meta = resolver.initialRouteMetaTag(panel);
        context.document = { querySelector: selector => selector === 'meta[name="initial-route"]'
          ? { content: route } : null };
        const rendererRoute = vm.runInContext('kst()', context, { timeout: 1000 });
        assert.equal(rendererRoute, route);
        emit('extension-route-selected', { uri, initialRoute: route, initialRouteMetaTag: meta,
          rendererInitialRoute: rendererRoute, origin: 'custom-editor-uri', navigationCount: 0 });
      });
      pending.push(promise);
      return promise;
    } },
  };
  Object.assign(context, { Ie: vscode, fPe: vscode });
  vm.runInContext(['E2', 'E7', 'E12', 'E13', 'E14', 'E15', 'E16', 'U1'].map(code).join('\n'), context, { timeout: 1000 });
  const resolver = vm.runInContext(`({${code('E3')},${code('E4')}})`, context, { timeout: 1000 });
  Object.assign(resolver, {
    conversationSummaryProvider: { getConversationSummary: async id => {
      assert.ok(threads.has(id)); return { summary: {} };
    } },
    extensionUri: 'synthetic-extension', editorPanels: panels,
    logger: { error: (...args) => emit('source-log-error', { args }) },
    registerOnDidDisposeForWebviewPanel() {},
    initializeWebview: async () => {}, // Host webview rendering is not launched.
    previewLoader: { fetchConversationPreviews: async () => new Map() },
    isPanelAlive: panel => panels.has(panel),
  });
  const restorer = vm.runInContext(`({${code('E1')}})`, context, { timeout: 1000 });
  await restorer.ensureRestoredConversationTabsResolved();
  await Promise.all(pending);
  const selectedUri = window.selectedUri;
  assert.equal(opened.length, 1, 'one custom editor per synthetic window');
  assert.equal(opened[0].uri.path, selectedUri.path);
  const route = [...panels.values()][0].initialRoute;
  const threadId = vm.runInContext('dI', context)(selectedUri).conversationId;
  const workspaceRoots = Array.from(vm.runInContext('aS()', context, { timeout: 1000 }));
  const discovery = vm.runInContext(`({${code('E8')}})`, context, { timeout: 1000 });
  discovery.ownerDiscoveryTimeoutMs = 1000;
  discovery.ipcClient = {
    waitUntilInitialized: async () => {},
    sendRequest: async (method, params, options) => {
      const owner = ownerByThread.get(params.conversationId) ?? null;
      emit('stub-ipc-owner-discovery', { method, params, options, mockedOwnerClientId: owner });
      return owner == null ? { resultType: 'error', error: 'no-client-found' }
        : { resultType: 'success', handledByClientId: owner };
    },
  };
  const owner = await discovery.findThreadOwner({ hostId: 'local', conversationId: threadId });
  const result = { ...identity, route, threadId, threadCwd: threads.get(threadId).cwd,
    workspaceRoots, ownerClientId: owner, streamRole: owner === window.clientId ? 'owner' : owner ? 'follower' : null,
    ownershipEvidence: 'stub IPC registry; actual discovery request executed', navigationCount: 0 };
  emit('restored-binding', result);
  return result;
}
