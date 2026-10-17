// One custom-editor persistence/restore cycle. Importing this module runs no cycle.
// Route-bearing persistence, MRU selection and tab hydration come from the pinned
// installed source. Host UI objects, URI APIs, storage backing and IPC are stubs.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';

const directory = path.dirname(fileURLToPath(import.meta.url));
const hash = value => createHash('sha256').update(value).digest('hex');
const clone = value => JSON.parse(JSON.stringify(value));

export class HostUri {
  constructor(parts) {
    Object.assign(this, { scheme: '', authority: '', path: '', query: '', fragment: '' }, parts);
  }
  static from(parts) { return new HostUri(parts); }
  static revive(parts) { return parts instanceof HostUri ? parts : new HostUri(parts); }
  static parse(value) {
    const url = new URL(value);
    return new HostUri({ scheme: url.protocol.slice(0, -1), authority: url.host,
      path: url.pathname, query: url.search.slice(1), fragment: url.hash.slice(1) });
  }
  toJSON() {
    const { scheme, authority, path, query, fragment } = this;
    return { scheme, authority, path, query, fragment };
  }
  toString() {
    return `${this.scheme}://${this.authority}${this.path}${this.query ? `?${this.query}` : ''}${this.fragment ? `#${this.fragment}` : ''}`;
  }
}

function loadSource() {
  const map = JSON.parse(fs.readFileSync(path.join(directory, 'restore-source-map.json')));
  const buffers = {};
  for (const [id, source] of Object.entries(map.sources)) {
    const bytes = fs.readFileSync(source.path);
    assert.equal(bytes.length, source.bytes, `${id} length changed`);
    assert.equal(hash(bytes), source.sha256, `${id} source changed`);
    buffers[id] = bytes;
  }
  const excerpts = {};
  for (const [id, item] of Object.entries(map.excerpts)) {
    const bytes = buffers[item.file].subarray(item.byte_start, item.byte_end_exclusive);
    assert.equal(hash(bytes), item.sha256, `${id} range changed`);
    assert.equal(bytes.toString('utf8'), item.text, `${id} excerpt differs`);
    excerpts[id] = item.text;
  }
  return { map, excerpts };
}

function createClient(excerpts) {
  // Disposable/event/UI identities provide the host API. They do not select,
  // overwrite or restore any URI, conversation ID, workspace ID or route.
  const disposable = { dispose() {} };
  const event = () => disposable;
  class Disposable { _register(value) { return value; } dispose() {} }
  class DisposableStore { add(value) { return value; } clear() {} dispose() {} }
  class Emitter { constructor() { this.event = event; } fire() {} }
  class EditorInput {}
  class WebviewInput extends EditorInput {}
  class CustomInput extends WebviewInput {
    constructor(options, webview, restoreOptions = {}) {
      super();
      this.resource = options.resource;
      this.viewType = options.viewType;
      this.providedId = options.viewType;
      this.iconPath = options.iconPath;
      this.webview = webview;
      this.extension = webview.extension;
      this.typeId = CustomInput.typeId;
      this.editorId = options.viewType;
      this.dirty = !!restoreOptions.startsDirty;
      this.backupId = restoreOptions.backupId;
      this.onWillDispose = event;
      this.onDidChangeDirty = event;
      this.onDidChangeLabel = event;
      this.onDidChangeCapabilities = event;
    }
    getName() { return 'Synthetic conversation'; }
    updateGroup(group) { this.group = group; }
    isDirty() { return this.dirty; }
    matches(other) { return this === other; }
  }
  class BranchNode {
    constructor(orientation, layout, styles, proportional, size, crossSize, ignored, children) {
      this.children = children.map(item => item.node);
    }
  }
  class LeafNode { constructor(view) { this.view = view; } }
  const registry = new Map();
  const context = vm.createContext({
    Ee: HostUri, I: HostUri,
    H0: EditorInput, zKt: WebviewInput, $2: CustomInput,
    we: Disposable, He: DisposableStore, ve: Emitter,
    Ct: { once: () => event },
    p4: BranchNode, m4: LeafNode,
    Ft: { isThemeIcon: value => typeof value?.id === 'string' },
    xu: class { constructor(value) { this.value = value; } },
    qu: items => items.filter(Boolean),
    pge: value => Object.keys(value).length === 0,
    ns: error => { throw error instanceof Error ? error : new Error(error); },
    kn: { as: () => ({ getEditorSerializer: value => registry.get(typeof value === 'string' ? value : value.typeId) }) },
    Wh: { EditorFactory: 'fixture-editor-factory' },
    Tk: class {}, ZE: class {}, xte: class {}, abe: class {}, MC: class {}, kF: class {}, g8: class {}, r9: class {}, nH: class {},
    jd: { BOTH: 2, ANY: 1 },
    vd: { getCanonicalUri: input => input.resource },
    Ac: (a, b) => a?.toString() === b?.toString(),
    kNe: value => value === 0 ? 1 : 0,
    ATt: value => !!value.children,
    Ma: { to: value => value + 1 },
    FixtureBase: class { saveState() {} },
  });
  const run = source => vm.runInContext(source, context, { timeout: 1000 });
  run(excerpts.custom_editor_type_id);
  run(`${excerpts.serializer_helpers};${excerpts.webview_overlay};${excerpts.group_shape};${excerpts.view_column}`);
  const BaseSerializer = run(`(${excerpts.serializer_base})`);
  context.ntn = BaseSerializer;
  const CustomSerializer = run(`(${excerpts.serializer_custom})`);
  const shouldPersist = run(`({${excerpts.persist_predicate}}).shouldPersist`);
  const webviewService = { createWebviewOverlay: options => ({
    origin: options.origin, options: options.options, contentOptions: options.contentOptions,
    extension: options.extension, state: undefined,
  }) };
  const instantiationService = { createInstance: (Constructor, ...args) => new Constructor(...args) };
  const serializer = new CustomSerializer({ shouldPersist }, instantiationService, webviewService);
  registry.set(CustomInput.typeId, serializer);
  const Group = run(`(${excerpts.editor_group})`);
  context.oNe = Group;
  Group.IDS = 0;
  const MementoStorage = run(`(${excerpts.memento_storage})`);
  context.wtr = MementoStorage;
  const Memento = run(`(${excerpts.memento_scope})`);
  context.gqt = Memento;
  run(excerpts.memento_static_scopes);
  const Grid = run(`(class TQn {${excerpts.grid_serialize_node}${excerpts.grid_serialize}${excerpts.grid_deserialize}})`);
  context.TQn = Grid;
  const gridFromState = (serialized, factory) => {
    const grid = new Grid();
    grid._deserialize(serialized.root, serialized.orientation, factory, serialized.height);
    return grid;
  };
  // Only layout node construction is stubbed. The installed recursive decoder
  // invokes the installed editor-part callback for each stored group.
  context.ASp = { createFromDeserializedGrid: gridFromState };
  const EditorPart = run(`(class Ybe extends FixtureBase {${excerpts.editorpart_persistence}${excerpts.editorpart_restore_groups}})`);
  context.Ybe = EditorPart;
  run(excerpts.editorpart_keys);
  const TabModel = run(`(class {${excerpts.tab_dto_methods}${excerpts.tab_model_create}})`);
  const StorageClient = run(`(${excerpts.storage_client})`);
  run(`var ${excerpts.storage_threshold};`);
  run(`var ${excerpts.tab_input_classes.slice(0, -1)};`);
  const ExtTab = run(`(${excerpts.ext_tab})`);
  context.m6 = ExtTab;
  const ExtTabGroup = run(`(${excerpts.ext_tab_group})`);
  return { Group, CustomInput, instantiationService, Memento, Grid, EditorPart, TabModel,
    StorageClient, ExtTabGroup, TabInputCustom: context.AO, TabInputText: context.IO };
}

function makeGroup(client, serialized) {
  return new client.Group(serialized, client.instantiationService, {
    getValue: () => undefined, onDidChangeConfiguration: () => ({ dispose() {} }),
  });
}

function snapshotTabs(groups) {
  return groups.map(group => ({ isActive: group.isActive, viewColumn: group.viewColumn,
    activeUri: group.activeTab?.input.uri.toString() ?? null,
    tabs: group.tabs.map(tab => ({ uri: tab.input.uri.toString(), isActive: tab.isActive,
      isPreview: tab.isPreview, viewType: tab.input.viewType })) }));
}

export async function runRestoreCycle({ windows, stateDir, eventSink = () => {} }) {
  assert.equal(windows.length, 2, 'exactly two synthetic windows required');
  assert.equal(new Set(windows.map(window => window.route)).size, 2, 'initial routes must differ');
  assert.equal(new Set(windows.map(window => window.workspaceId)).size, 2, 'workspace IDs must differ');
  assert.equal(fs.readdirSync(stateDir).length, 0, 'state directory must be empty');
  const { map, excerpts } = loadSource();
  const client = createClient(excerpts);
  const emit = (window, stage, detail = {}) => eventSink(stage, { component: 'cursor-custom-editor-host',
    windowId: window.windowId, clientId: window.clientId, workspaceId: window.workspaceId,
    membership: clone(window.membership), ...detail });
  const makeStorage = async window => {
    assert.match(window.workspaceId, /^[a-z0-9-]+$/);
    const filename = path.join(stateDir, `${window.workspaceId}.json`);
    const channel = { async call(method, args) {
      assert.equal(args.workspace.id, window.workspaceId, 'native storage client changed workspace');
      assert.equal(args.profile, undefined, 'profile storage is forbidden');
      emit(window, 'storage-ipc', { method, scope: 'workspace', requestedWorkspaceId: args.workspace.id });
      const data = fs.existsSync(filename) ? JSON.parse(fs.readFileSync(filename)) : {};
      if (method === 'getItems') return Object.entries(data);
      assert.equal(method, 'updateItems', 'unapproved storage API');
      for (const [key, value] of args.insert ?? []) data[key] = value;
      for (const key of args.delete ?? []) delete data[key];
      fs.writeFileSync(filename, `${JSON.stringify(data)}\n`, { mode: 0o600 });
    } };
    const database = new client.StorageClient(channel, undefined, { id: window.workspaceId });
    const items = await database.getItems();
    const pending = new Map();
    const deleted = new Set();
    return {
      getObject(key, scope, fallback) { assert.equal(scope, 1); return items.has(key) ? JSON.parse(items.get(key)) : fallback; },
      get(key, scope) { assert.equal(scope, 1); return items.get(key); },
      store(key, value, scope) { assert.equal(scope, 1); const encoded = JSON.stringify(value); items.set(key, encoded); pending.set(key, encoded); },
      remove(key, scope) { assert.equal(scope, 1); items.delete(key); deleted.add(key); },
      async flush() { await database.updateItems({ insert: pending, delete: deleted }); },
      filename,
    };
  };
  const inputs = [];
  for (const window of windows) {
    assert.match(window.route, /^\/local\/synthetic-thread-[a-z0-9-]+$/);
    const uri = HostUri.from({ scheme: 'openai-codex', authority: 'route', path: window.route });
    const model = makeGroup(client);
    const editor = new client.CustomInput({ resource: uri, viewType: 'chatgpt.conversationEditor' }, {
      origin: `synthetic-origin-${window.windowId}`, options: { retainContextWhenHidden: true }, contentOptions: {},
    });
    editor.updateGroup(model.id);
    // Explicit fixture initialization only. Restoration cannot reuse these
    // objects: the next phase reads the saved bytes into new groups and inputs.
    model.editors = [editor]; model.mru = [editor]; model.selection = [editor];
    const storage = await makeStorage(window);
    const memento = new client.Memento('workbench.parts.editor', storage);
    const part = new client.EditorPart();
    part.workspaceMemento = memento.getMemento(1, 0);
    part.profileMemento = {};
    part._activeGroup = model;
    part.mostRecentActiveGroups = [model.id];
    part.isEmpty = false;
    const grid = new client.Grid();
    Object.assign(grid, { orientation: 0, width: 800, height: 600,
      getViews: () => ({ box: { width: 800, height: 600 }, children: [
        { box: { width: 800, height: 600 }, view: { toJSON: () => model.serialize() } },
      ] }) });
    part.gridWidget = grid;
    emit(window, 'initial-selection', { routeOrigin: 'fixture-custom-editor-uri', route: window.route,
      uri: uri.toString(), activeGroup: model.id, beforeNavigation: true });
    part.saveState();
    memento.saveMemento();
    await storage.flush();
    const savedState = clone(part.workspaceMemento['editorpart.state']);
    inputs.push({ window, savedState, filename: storage.filename });
    emit(window, 'persisted', { routeOrigin: 'native-custom-editor-serializer', savedState, beforeNavigation: true });
  }
  // A new client context discards the in-memory memento caches, editor models
  // and tab objects. Both windows hydrate from the same isolated backing store.
  const restoredClient = createClient(excerpts);
  const restored = [];
  for (const { window, savedState, filename } of inputs) {
    const storage = await makeStorage(window);
    const memento = new restoredClient.Memento('workbench.parts.editor', storage);
    const part = new restoredClient.EditorPart();
    part.workspaceMemento = memento.getMemento(1, 0);
    const state = part.loadState();
    assert.deepEqual(clone(state), savedState, 'native memento state changed on hydration');
    const groups = [];
    part.mostRecentActiveGroups = state.mostRecentActiveGroups;
    part.doCreateGroupView = serialized => {
      const group = makeGroup(restoredClient, serialized);
      groups.push(group);
      return group;
    };
    part.doSetGroupActive = group => { part._activeGroup = group; };
    part.getGroup = id => groups.find(group => group.id === id);
    part.doSetGridWidget = grid => { part.gridWidget = grid; };
    part.doCreateGridControlWithState(state.serializedGrid, state.activeGroup);
    const tabModel = new restoredClient.TabModel();
    tabModel._editorGroupsService = { groups, activeGroup: part._activeGroup,
      getGroups: () => groups, getGroup: id => groups.find(group => group.id === id) };
    tabModel._groupLookup = new Map();
    tabModel._tabInfoLookup = new Map();
    tabModel._logService = { warn: message => { throw new Error(message); } };
    let dto;
    tabModel._proxy = { $acceptEditorTabModel: value => { dto = value; } };
    tabModel._createTabsModel();
    const activeGroupId = dto.find(group => group.isActive).groupId;
    const tabGroups = dto.map(group => new restoredClient.ExtTabGroup(group, () => activeGroupId).apiObject);
    const selectedUri = tabGroups.find(group => group.isActive).activeTab.input.uri;
    emit(window, 'restored-before-navigation', { routeOrigin: 'workspace-memento/custom-editor-deserialize/tab-api',
      route: selectedUri.path, uri: selectedUri.toString(), activeGroup: activeGroupId,
      tabs: snapshotTabs(tabGroups), beforeNavigation: true });
    restored.push({ ...window, uri: selectedUri, selectedUri, tabGroups,
      savedState, storageFilename: path.basename(filename), routeOrigin: 'workspace-memento/custom-editor-deserialize/tab-api' });
  }
  return { windows: restored,
    distinctBeforeNavigation: new Set(restored.map(window => window.selectedUri.toString())).size === 2,
    snapshots: restored.map(window => ({ windowId: window.windowId, initialRoute: window.route,
      savedRoute: JSON.parse(window.savedState.serializedGrid.root.data[0].data.editors[0].value).editorResource.path,
      savedState: window.savedState, restoredRoute: window.selectedUri.path, tabs: snapshotTabs(window.tabGroups) })),
    sourceHashes: Object.fromEntries(Object.entries(map.sources).map(([key, source]) => [key, source.sha256])),
    limitations: map.limitations,
  };
}
