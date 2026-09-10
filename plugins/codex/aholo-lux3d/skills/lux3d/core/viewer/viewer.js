import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const data = JSON.parse(document.getElementById('lux3d-data').textContent);
const manifest = data.manifest;
const t = (key, values = {}) => data.messages[key].replace(/\{(\w+)\}/g, (_, name) => {
  if (!Object.hasOwn(values, name)) throw new Error(`Missing translation parameter: ${key}.${name}`);
  return String(values[name]);
});
const artifacts = new Map(manifest.artifacts.map(value => [value.id, value]));
const tasks = new Map(manifest.tasks.map(value => [value.id, value]));
const attempts = new Map(manifest.attempts.map(value => [value.id, value]));
const views = [];
const downloadUrls = new Set();
let renderer;
let environment;
let draco;
let ktx2;
let loader;

function element(tag, text, className) {
  const result = document.createElement(tag);
  if (text !== undefined) result.textContent = text;
  if (className) result.className = className;
  return result;
}

function bytes(base64) {
  const decoded = atob(base64);
  return Uint8Array.from(decoded, character => character.charCodeAt(0));
}

function field(list, label, value) {
  const wrapper = element('div');
  const unavailable = value === null || value === undefined;
  wrapper.append(element('dt', label), element('dd', unavailable ? t('unavailable') : String(value), unavailable ? 'unavailable' : undefined));
  list.append(wrapper);
}

function localDuration(attempt) {
  return attempt?.localDurationMs == null ? null : t('durationSeconds', { seconds: attempt.localDurationMs / 1000 });
}

function downloadLink(artifact) {
  const label = t('download', { format: artifact.format.toUpperCase() });
  const link = element('a', label);
  link.setAttribute('aria-label', label);
  link.href = '#';
  link.download = artifact.path.split('/').pop();
  link.addEventListener('click', event => {
    if (!data.assets[artifact.id]) { event.preventDefault(); return; }
    if (link.href.startsWith('blob:')) return;
    const url = URL.createObjectURL(new Blob([bytes(data.assets[artifact.id])], { type: 'application/octet-stream' }));
    downloadUrls.add(url);
    link.href = url;
  });
  return link;
}

function initializeRenderer() {
  if (renderer) return;
  renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('viewer-canvas'), antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  const pmrem = new THREE.PMREMGenerator(renderer);
  const room = new RoomEnvironment();
  environment = pmrem.fromScene(room);
  room.dispose(); pmrem.dispose();
  const manager = new THREE.LoadingManager();
  manager.setURLModifier(url => {
    if (Object.hasOwn(data.decoders, url)) return data.decoders[url];
    if (url.startsWith('data:') || url.startsWith('blob:')) return url;
    throw new Error('RESOURCE_NOT_EMBEDDED');
  });
  draco = new DRACOLoader(manager).setDecoderPath({
    js: 'lux3d-embedded/draco/draco_wasm_wrapper.js', wasm: 'lux3d-embedded/draco/draco_decoder.wasm',
  });
  ktx2 = new KTX2Loader(manager).setTranscoderPath('lux3d-embedded/basis/').detectSupport(renderer);
  loader = new GLTFLoader(manager).setDRACOLoader(draco).setKTX2Loader(ktx2).setMeshoptDecoder(MeshoptDecoder);
  renderer.setAnimationLoop(render);
}

function fit(view) {
  const rect = view.viewport.getBoundingClientRect();
  const vertical = THREE.MathUtils.degToRad(view.camera.fov) / 2;
  const horizontal = Math.atan(Math.tan(vertical) * rect.width / rect.height);
  // A bounding sphere fits exactly at r/sin(half-FOV). The extra 5% is display padding.
  const distance = view.sphere.radius / Math.sin(Math.min(vertical, horizontal)) * 1.05;
  view.camera.position.copy(view.sphere.center).addScaledVector(new THREE.Vector3(1, 0.65, 1).normalize(), distance);
  view.controls.minDistance = view.sphere.radius * 1.05;
  view.controls.maxDistance = distance * 4;
  // Clip bounds cover the whole object throughout the allowed orbit/zoom range.
  view.camera.near = (view.controls.minDistance - view.sphere.radius) / 2;
  view.camera.far = view.controls.maxDistance + view.sphere.radius * 2;
  view.controls.target.copy(view.sphere.center);
  view.controls.update();
}

async function addPreview(viewport, artifact) {
  const notice = element('div', t('loading'), 'preview-notice');
  viewport.append(notice);
  viewport.dataset.previewState = 'loading';
  try {
    initializeRenderer();
    const gltf = await loader.parseAsync(bytes(data.assets[artifact.id]).buffer, '');
    const sphere = new THREE.Box3().setFromObject(gltf.scene, true).getBoundingSphere(new THREE.Sphere());
    if (!Number.isFinite(sphere.radius) || sphere.radius <= 0) throw new Error('NO_RENDERABLE_GEOMETRY');
    const scene = new THREE.Scene();
    // Transparent WebGL preserves the neutral CSS studio background. Asset materials are unchanged.
    scene.environment = environment.texture;
    scene.add(gltf.scene);
    const camera = new THREE.PerspectiveCamera(38);
    const controls = new OrbitControls(camera, viewport);
    controls.addEventListener('change', () => { viewport.dataset.interactions = String(Number(viewport.dataset.interactions || 0) + 1); });
    viewport.addEventListener('wheel', event => event.preventDefault(), { passive: false });
    const reset = element('button', t('resetView'), 'reset');
    reset.type = 'button';
    const view = { viewport, scene, camera, controls, sphere, notice, gltf };
    reset.addEventListener('click', () => fit(view));
    const tools = element('div', undefined, 'stage-tools');
    tools.append(element('span', t('orbitHint'), 'stage-hint'), reset);
    viewport.append(element('span', t('localPreview'), 'stage-label'), tools);
    fit(view);
    views.push(view);
  } catch {
    viewport.dataset.previewState = 'error';
    notice.textContent = t('previewError');
  }
}

function render() {
  const ratio = renderer.getPixelRatio();
  if (renderer.domElement.width !== Math.floor(innerWidth * ratio) || renderer.domElement.height !== Math.floor(innerHeight * ratio)) {
    renderer.setSize(innerWidth, innerHeight);
  }
  renderer.domElement.style.transform = `translateY(${window.scrollY}px)`;
  renderer.setScissorTest(false);
  renderer.setClearColor(0, 0);
  renderer.clear();
  renderer.setScissorTest(true);
  for (const view of views) {
    const rect = view.viewport.getBoundingClientRect();
    if (rect.bottom <= 0 || rect.top >= innerHeight || rect.right <= 0 || rect.left >= innerWidth) continue;
    view.camera.aspect = rect.width / rect.height;
    view.camera.updateProjectionMatrix();
    const left = Math.max(0, rect.left), bottom = Math.max(0, innerHeight - rect.bottom);
    renderer.setScissor(left, bottom, Math.min(rect.right, innerWidth) - left, Math.min(innerHeight - rect.top, innerHeight) - bottom);
    renderer.setViewport(rect.left, innerHeight - rect.bottom, rect.width, rect.height);
    renderer.render(view.scene, view.camera);
    view.viewport.dataset.previewState = 'ready';
    view.notice.hidden = true;
  }
}

function card(item, index) {
  const result = element('article', undefined, 'card');
  result.id = `item-${item.id}`;
  const heading = element('div', undefined, 'card-heading');
  const label = element('div', undefined, 'asset-heading');
  label.append(element('span', String(index + 1).padStart(2, '0'), 'asset-index'), element('h2', item.label));
  heading.append(label, element('span', t(item.status === 'complete' ? 'assetsReady' : 'incomplete'), `badge ${item.status}`));
  const viewport = element('div', undefined, 'viewport');
  viewport.tabIndex = 0; viewport.setAttribute('aria-label', t('itemPreview', { label: item.label }));
  const selected = attempts.get(item.selectedAttemptId);
  const task = tasks.get(selected?.taskRef);
  const metadata = element('dl', undefined, 'metadata');
  field(metadata, t('taskId'), task?.taskId);
  field(metadata, t('taskCreated'), task?.createdAt);
  field(metadata, t('localStart'), selected?.localStartedAt);
  field(metadata, t('localDuration'), localDuration(selected));
  const downloads = element('div', undefined, 'downloads');
  for (const id of item.artifactIds) downloads.append(downloadLink(artifacts.get(id)));
  const info = element('div', undefined, 'asset-info');
  info.append(metadata, downloads);
  const body = element('div', undefined, 'card-body');
  body.append(viewport, info);
  result.append(heading, body);
  const preview = item.artifactIds.map(id => artifacts.get(id)).find(artifact => artifact.format === 'glb');
  if (preview) void addPreview(viewport, preview);
  else { viewport.dataset.previewState = 'unavailable'; viewport.append(element('div', t('noGlb'), 'preview-notice')); }
  return result;
}

function sceneCard() {
  const scene = manifest.scene;
  if (scene.status !== 'ready') {
    const message = element('div', undefined, 'scene-message');
    const symbol = element('span', '◇', 'scene-symbol');
    symbol.setAttribute('aria-hidden', 'true');
    const copy = element('div');
    copy.append(element('h2', t('assembledScene')), element('div', scene.status === 'not-requested' ? t('sceneNotRequested') : t('sceneIncomplete', {
      reason: scene.failureCode === 'scene-validation-failed' ? t('sceneValidationFailed') : scene.reason,
    }), 'scene-reason'));
    message.append(symbol, copy);
    return message;
  }
  const result = element('article', undefined, 'card scene-card');
  const heading = element('div', undefined, 'card-heading');
  heading.append(element('h2', t('assembledScene')), element('span', t('validatedExport'), 'badge'));
  const viewport = element('div', undefined, 'viewport');
  viewport.tabIndex = 0;
  viewport.setAttribute('aria-label', t('scenePreview'));
  const metadata = element('dl', undefined, 'metadata');
  field(metadata, t('executionEvidence'), t(scene.execution.kind === 'development-fixture' ? 'developmentFixture' : 'suppliedRecord'));
  field(metadata, t('tool'), scene.execution.toolName);
  field(metadata, t('executionTime'), scene.execution.executedAt);
  field(metadata, t('toolCallId'), scene.execution.callId);
  const sourceList = element('ul');
  for (const source of scene.sources) {
    const item = manifest.items.find(item => item.id === source.itemId);
    const attempt = attempts.get(source.attemptId);
    const task = tasks.get(attempt.taskRef);
    const entry = element('li');
    const link = element('a', t('sceneSource', { label: item.label, attempt: source.attemptId, task: task?.taskId ?? t('unavailable') }));
    link.href = `#item-${source.itemId}`;
    entry.append(link); sourceList.append(entry);
  }
  const downloads = element('div', undefined, 'downloads');
  downloads.append(downloadLink(artifacts.get(scene.artifactId)), downloadLink(artifacts.get(scene.evidenceArtifactId)));
  result.append(heading, viewport, metadata, sourceList, downloads);
  void addPreview(viewport, artifacts.get(scene.artifactId));
  return result;
}

for (const [value, label, note] of [
  [manifest.items.length, t('individualItems'), t('inCollection')],
  [manifest.tasks.length, t('uniqueTasks'), t('countedOnce')],
]) {
  const metric = element('div', undefined, 'metric');
  metric.append(element('span', String(value), 'metric-value'), element('span', label, 'metric-label'), element('span', note, 'metric-note'));
  document.getElementById('summary').append(metric);
}
const status = document.getElementById('delivery-status');
status.classList.toggle('complete', manifest.status === 'complete');
status.append(element('strong', t(manifest.status === 'complete' ? 'deliveryComplete' : 'unverifiedSteps')),
  element('span', t(manifest.status === 'complete' ? 'completeNote' : 'incompleteNote')));
const grid = document.getElementById('items');
grid.dataset.count = String(manifest.items.length);
document.getElementById('asset-count').textContent = manifest.items.length;
document.getElementById('attempt-count').textContent = manifest.attempts.length;
manifest.items.forEach((item, index) => grid.append(card(item, index)));
const manifestLink = document.getElementById('manifest-download');
const manifestUrl = URL.createObjectURL(new Blob([JSON.stringify(manifest, null, 2) + '\n'], { type: 'application/json' }));
manifestLink.href = manifestUrl;
downloadUrls.add(manifestUrl);
document.getElementById('scene-section').append(sceneCard());
const notices = element('details');
notices.append(element('summary', t('thirdPartyNotices')), element('pre', data.notices));
document.querySelector('footer').append(notices);
for (const attempt of manifest.attempts) {
  const task = tasks.get(attempt.taskRef);
  const row = element('tr');
  for (const value of [attempt.id, task ? `${task.taskId} / ${task.region}` : t('unavailable'), t(`state.${attempt.status}`), attempt.localStartedAt ?? t('unavailable'), attempt.localCompletedAt ?? t('unavailable'), localDuration(attempt) ?? t('unavailable')]) row.append(element('td', value));
  const originals = element('td');
  for (const id of attempt.artifactIds) originals.append(downloadLink(artifacts.get(id)));
  if (!attempt.artifactIds.length) originals.textContent = t('noOriginals');
  row.append(originals);
  document.getElementById('history').append(row);
}
window.addEventListener('pagehide', () => {
  renderer?.setAnimationLoop(null);
  for (const view of views) {
    view.controls.dispose();
    view.scene.traverse(object => {
      object.geometry?.dispose();
      const materials = Array.isArray(object.material) ? object.material : object.material ? [object.material] : [];
      for (const material of materials) {
        for (const value of Object.values(material)) if (value?.isTexture) { value.source?.data?.close?.(); value.dispose(); }
        material.dispose();
      }
    });
  }
  environment?.dispose(); draco?.dispose(); ktx2?.dispose(); renderer?.dispose();
  for (const url of downloadUrls) URL.revokeObjectURL(url);
});
