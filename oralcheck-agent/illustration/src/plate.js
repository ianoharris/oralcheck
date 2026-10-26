// Textbook-illustration renderer for the OralCheck head model (prototype, 23 Oct).
//
// Same Z-Anatomy geometry as anatomy3d/, drawn the way medical illustration
// plates are drawn instead of the way a game draws skin: soft wrapped light,
// darker edges, flat pale cut surfaces, a thin outline round every structure,
// a little contact shadow where parts meet, and the head kept only as a faded
// context. No photo textures. Orthographic camera, so a plate reads as a plate.
//
// window.pl is the scripting surface (see render_plate.py).
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";

THREE.ColorManagement.enabled = false;     // colours below are screen colours, used as they are

// base colour, cut colour, wetness (0 dry .. 1 glossy)
const STYLE = {
  bone:       ["#e6d9bf", "#f3ead6", 0.0],
  tooth:      ["#f4efe4", "#f8f3e8", 0.5],
  cartilage:  ["#a6c0d4", "#c3d6e4", 0.2],
  muscle:     ["#bf5a52", "#d68377", 0.15],
  tongue:     ["#d86f78", "#e48c92", 0.6],
  mucosa:     ["#e38f92", "#eeaaa9", 0.7],
  softpalate: ["#d7797f", "#e3969a", 0.6],
  tonsil:     ["#c96679", "#d6838f", 0.6],
  gland:      ["#e6c07f", "#efd5a2", 0.1],
  brain:      ["#e9d8d2", "#f1e4df", 0.0],
  lip:        ["#cf7272", "#e19590", 0.5],
};
const GROUPS = Object.keys(STYLE);
const PAPER = new THREE.Color("#f4f2ef");

function groupOf(name, cls) {
  if (/^(Oropharynx|Nasopharynx|Laryngopharynx)$/.test(name)) return null;   // the atlas's blocks for the airway spaces
  if (cls === "tongue" || /^(Genioglossus|Hyoglossus|Styloglossus)/.test(name)) return "tongue";
  if (/^(Soft palate|Uvula of palate)$/.test(name)) return "softpalate";
  if (cls === "oral" || cls === "gingiva" || /^(Mucosa of nasal cavity|Trachea|Oesophagus)$/.test(name)) return "mucosa";
  if (cls === "mucosa") return null;                                          // lung tops and pleura at the cut-off
  if (/^(tooth|bone|cartilage|muscle|gland|brain|tonsil|lip)$/.test(cls)) return cls;
  return null;                                                                // vessels, nerves, nodes, eyes, fascia: not in a plate
}

const VERT = /* glsl */ `
#include <clipping_planes_pars_vertex>
varying vec3 vN; varying vec3 vW;
void main() {
  vec4 wp = modelMatrix * vec4(position, 1.0); vW = wp.xyz;
  vN = normalize(normalMatrix * normal);
  vec4 mvPosition = viewMatrix * wp;
  gl_Position = projectionMatrix * mvPosition;
  #include <clipping_planes_vertex>
}`;
const FRAG = /* glsl */ `
#include <clipping_planes_pars_fragment>
uniform vec3 uColor, uCut, uPaper, uTint; uniform float uWet, uFade, uTintK;
varying vec3 vN; varying vec3 vW;
float h3(vec3 p){ return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
float vnoise(vec3 p){ vec3 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
  return mix(mix(mix(h3(i), h3(i+vec3(1,0,0)), f.x), mix(h3(i+vec3(0,1,0)), h3(i+vec3(1,1,0)), f.x), f.y),
             mix(mix(h3(i+vec3(0,0,1)), h3(i+vec3(1,0,1)), f.x), mix(h3(i+vec3(0,1,1)), h3(i+vec3(1,1,1)), f.x), f.y), f.z); }
void main() {
  #include <clipping_planes_fragment>
  vec3 col;
  if (!gl_FrontFacing) {
    // a back face seen through the cut is the cut surface: flat, pale, with a faint grain
    col = uCut * (0.975 + 0.05 * vnoise(vW * 900.0));
  } else {
    vec3 N = normalize(vN), V = vec3(0.0, 0.0, 1.0);
    vec3 L = normalize(vec3(-0.45, 0.65, 0.62));                // key from upper left, as in most plates
    float d = clamp((dot(N, L) + 0.45) / 1.45, 0.0, 1.0);       // wrapped, so shadows stay soft and coloured
    float sky = 0.5 + 0.5 * N.y;
    float edge = pow(1.0 - clamp(N.z, 0.0, 1.0), 2.2);          // painted edge falloff
    col = uColor * (0.60 + 0.34 * d + 0.08 * sky);
    col = mix(col, col * vec3(0.78, 0.66, 0.70), edge * 0.55);   // edges go deeper and a little cooler
    float spec = pow(max(dot(reflect(-L, N), V), 0.0), 28.0);
    col += vec3(1.0) * spec * uWet * 0.28;
    col *= 0.985 + 0.03 * vnoise(vW * 600.0);
  }
  col = mix(col, uTint, uTintK);
  col = mix(col, uPaper, uFade);
  gl_FragColor = vec4(col, 1.0);
}`;
const ID_FRAG = /* glsl */ `
#include <clipping_planes_pars_fragment>
uniform vec3 uId;
void main() {
  #include <clipping_planes_fragment>
  gl_FragColor = vec4(uId, 1.0); }`;
const ID_VERT = /* glsl */ `
#include <clipping_planes_pars_vertex>
void main() { vec4 mvPosition = modelViewMatrix * vec4(position, 1.0); gl_Position = projectionMatrix * mvPosition;
  #include <clipping_planes_vertex>
}`;

// outlines from the id and depth buffers, plus a small screen-space contact shadow
const POST_FRAG = /* glsl */ `
uniform sampler2D tCol, tId, tDepth; uniform vec2 uPx; uniform float uLine, uAO;
varying vec2 vUv;
float dep(vec2 uv){ return texture2D(tDepth, uv).x; }
void main() {
  vec4 c = texture2D(tCol, vUv); vec3 id = texture2D(tId, vUv).rgb; float d0 = dep(vUv);
  float line = 0.0;
  for (int i = 0; i < 8; i++) {
    float a = float(i) * 0.785398; vec2 o = vec2(cos(a), sin(a)) * uPx * uLine;
    vec3 idn = texture2D(tId, vUv + o).rgb; float dn = dep(vUv + o);
    bool other = distance(idn, id) > 0.002;
    if (other && (d0 <= dn + 0.00002)) line = max(line, 1.0);           // the nearer side of a boundary carries the line
    if (!other && abs(dn - d0) > 0.004) line = max(line, 0.55);         // folds inside one structure
  }
  float occ = 0.0;
  for (int i = 0; i < 16; i++) {
    float a = float(i) * 0.3927 + 0.2, r = (4.0 + 10.0 * fract(float(i) * 0.618)) * uAO;
    float dn = dep(vUv + vec2(cos(a), sin(a)) * uPx * r);
    occ += clamp((d0 - dn) * 160.0, 0.0, 1.0);
  }
  occ /= 16.0;
  vec3 col = c.rgb * (1.0 - 0.38 * occ);
  col = mix(col, col * vec3(0.42, 0.33, 0.33), line * 0.85);
  gl_FragColor = vec4(col, c.a);
}`;

const W0 = 1200, H0 = 1200;
const renderer = new THREE.WebGLRenderer({ antialias: false, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W0, H0); renderer.localClippingEnabled = true;
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;         // colours above are authored as screen colours
renderer.setClearColor(0x000000, 0);
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.001, 10);
const meshes = [], byName = new Map();
const clip = new THREE.Plane(new THREE.Vector3(1, 0, 0), 0), clip2 = new THREE.Plane(new THREE.Vector3(-1, 0, 0), 0);
let clipOn = false, slab = 0;
const planes = () => (clipOn ? (slab ? [clip, clip2] : [clip]) : []);
let SS = 2;                                                      // supersampling for the final image
let rtCol, rtId, post, postScene, postCam;

function makeTargets(w, h) {
  const dt = new THREE.DepthTexture(w, h); dt.type = THREE.FloatType;
  rtCol = new THREE.WebGLRenderTarget(w, h, { depthTexture: dt, samples: 0, colorSpace: THREE.LinearSRGBColorSpace });
  rtId = new THREE.WebGLRenderTarget(w, h, { magFilter: THREE.NearestFilter, minFilter: THREE.NearestFilter });
  post = new THREE.ShaderMaterial({
    uniforms: { tCol: { value: rtCol.texture }, tId: { value: rtId.texture }, tDepth: { value: dt }, uPx: { value: new THREE.Vector2(1 / w, 1 / h) },
      uLine: { value: 1.6 * SS }, uAO: { value: 1.0 * SS } },
    vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }", fragmentShader: POST_FRAG,
    transparent: true,
  });
  postScene = new THREE.Scene(); postScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), post)); postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
}

function material(group) {
  const [c, cut, wet] = STYLE[group];
  const m = new THREE.ShaderMaterial({
    uniforms: { uColor: { value: new THREE.Color(c) }, uCut: { value: new THREE.Color(cut) }, uPaper: { value: PAPER.clone() }, uWet: { value: wet },
      uFade: { value: 0 }, uTint: { value: new THREE.Color("#2bb3a7") }, uTintK: { value: 0 } },
    vertexShader: VERT, fragmentShader: FRAG, side: THREE.DoubleSide, clipping: true,
  });
  return m;
}

// ---- jaw: the same rig as anatomy3d/src/main.js, without the skin and lips -------------
const JAW_MAX = 0.42, pivot = new THREE.Vector3(), rigged = [];
const RIGID = /^(Mandible|Lower (?!lip|labial|gingiva).*(incisor|canine|premolar|molar).*|Lower gingiva|Lower lip|Lower labial mucosa|Floor of mouth mucosa|Sublingual gland.*|Geniohyoid.*|Mylohyoid.*|Anterior belly of digastric.*|Genioglossus.*|Mentalis.*|Depressor labii.*)$/;
function rigJaw() {
  const mand = byName.get("Mandible"); if (!mand) return;
  const pts = [], v = new THREE.Vector3();
  for (const m of mand) { const p = m.geometry.attributes.position; for (let i = 0; i < p.count; i++) pts.push(v.fromBufferAttribute(p, i).applyMatrix4(m.matrixWorld).clone()); }
  pts.sort((a, b) => b.y - a.y);
  const top = pts.slice(0, Math.max(10, Math.floor(pts.length * 0.01)));
  pivot.copy(top.reduce((a, b) => a.add(b), new THREE.Vector3()).divideScalar(top.length)); pivot.x = 0;
  for (const m of meshes) {
    const n = m.userData.name; let weight = null;
    if (RIGID.test(n)) weight = () => 1;
    else if (n === "Tongue") weight = (q) => 0.12 + 0.45 * THREE.MathUtils.smoothstep(q.z, 0.03, 0.075);
    else if (/^Buccal mucosa/.test(n)) weight = (q) => THREE.MathUtils.smoothstep(-q.y, -1.542, -1.515);
    const ahh = n === "Tongue" ? (q) => THREE.MathUtils.smoothstep(q.y, 1.512, 1.537) * THREE.MathUtils.smoothstep(-q.z, -0.075, -0.035) : null;
    if (!weight) continue;
    const g = m.geometry, p = g.attributes.position, nrm = g.attributes.normal, mw = m.matrixWorld.clone(), nm = new THREE.Matrix3().getNormalMatrix(mw);
    const rest = [], w = [], restN = [], dw = [];
    for (let i = 0; i < p.count; i++) { const q = v.fromBufferAttribute(p, i).applyMatrix4(mw).clone(); rest.push(q); w.push(weight(q)); dw.push(ahh ? ahh(q) : 0); }
    if (nrm) for (let i = 0; i < nrm.count; i++) restN.push(new THREE.Vector3(nrm.getX(i), nrm.getY(i), nrm.getZ(i)).applyMatrix3(nm).normalize());
    g.setAttribute("position", new THREE.Float32BufferAttribute(rest.flatMap((q) => [q.x, q.y, q.z]), 3));
    if (nrm) g.setAttribute("normal", new THREE.Float32BufferAttribute(restN.flatMap((q) => [q.x, q.y, q.z]), 3));
    scene.attach(m); m.position.set(0, 0, 0); m.quaternion.identity(); m.scale.set(1, 1, 1); m.updateMatrixWorld(true);
    const idx = []; for (let i = 0; i < rest.length; i++) if (w[i] > 0 || dw[i] > 0) idx.push(i);
    rigged.push({ m, rest, idx, w, dw: ahh ? dw : null, restN: nrm ? restN : null });
  }
}
function openJaw(k, ahh = 0) {
  const q = new THREE.Vector3(), axis = new THREE.Vector3(1, 0, 0), rot = new THREE.Quaternion();
  for (const r of rigged) {
    const p = r.m.geometry.attributes.position, nrm = r.m.geometry.attributes.normal;
    for (const i of r.idx) {
      rot.setFromAxisAngle(axis, k * JAW_MAX * r.w[i]);
      q.copy(r.rest[i]).sub(pivot).applyQuaternion(rot).add(pivot);
      if (r.dw) { q.y -= 0.011 * ahh * r.dw[i]; q.z += 0.003 * ahh * r.dw[i]; }
      p.setXYZ(i, q.x, q.y, q.z);
      if (r.restN && nrm) { q.copy(r.restN[i]).applyQuaternion(rot); nrm.setXYZ(i, q.x, q.y, q.z); }
    }
    p.needsUpdate = true; if (nrm) nrm.needsUpdate = true; r.m.geometry.computeBoundingSphere(); r.m.geometry.computeBoundingBox();
  }
}

// ---- drawing ----------------------------------------------------------------------
const idColors = new Map();
function drawPass(kind) {
  for (const m of meshes) {
    if (kind === "id") { m.userData.saved = m.material; m.material = m.userData.idMat; }
    m.material.clippingPlanes = m.userData.noClip ? [] : planes();
  }
  renderer.setRenderTarget(kind === "id" ? rtId : rtCol);
  renderer.setClearColor(0x000000, 0); renderer.clear();
  renderer.render(scene, camera);
  if (kind === "id") for (const m of meshes) m.material = m.userData.saved;
}
function render() {
  drawPass("col"); drawPass("id");
  renderer.setRenderTarget(null); renderer.setClearColor(0x000000, 0); renderer.clear();
  renderer.render(postScene, postCam);
  return renderer.domElement.toDataURL("image/png");
}

window.pl = {
  size(w, h, ss = 2) {
    SS = ss; renderer.setSize(w * ss, h * ss); renderer.domElement.style.width = w + "px";
    makeTargets(w * ss, h * ss);
  },
  // camera: dir points from the target to the camera; height is the view height in metres
  view({ dir = [-1, 0, 0], up = [0, 1, 0], target = [0, 1.52, 0.03], height = 0.3 }) {
    const W = renderer.domElement.width, H = renderer.domElement.height, h = height / 2, w = h * W / H;
    Object.assign(camera, { left: -w, right: w, top: h, bottom: -h }); camera.updateProjectionMatrix();
    const t = new THREE.Vector3(...target), d = new THREE.Vector3(...dir).normalize();
    camera.position.copy(t).addScaledVector(d, 1.0); camera.up.set(...up); camera.lookAt(t); camera.near = 0.5; camera.far = 1.5; camera.updateProjectionMatrix();
  },
  // keep everything with x >= offset (along the plane's normal), or only a slab that thick past it
  cut(spec) {
    clipOn = !!spec; if (!spec) return;
    clip.normal.set(...(spec.normal || [1, 0, 0])); clip.constant = -(spec.offset || 0);
    slab = spec.slab || 0; clip2.normal.copy(clip.normal).negate(); clip2.constant = (spec.offset || 0) + slab;
  },
  // show: {group: {fade, tint}} ; groups not listed are hidden; hide: regex of names to leave out
  show(spec, hide) {
    const re = hide ? new RegExp(hide, "i") : null;
    for (const m of meshes) {
      if (m.userData.group === "lesion") continue;
      const s = spec[m.userData.group];
      m.visible = !!s && !(re && re.test(m.userData.name));
      if (!s) continue;
      const u = m.material.uniforms; u.uFade.value = s.fade || 0; u.uTintK.value = 0;
    }
  },
  tint(pattern, k = 0.55, color = "#2bb3a7") {
    const re = new RegExp(pattern, "i");
    for (const m of meshes) if (re.test(m.userData.name)) { m.material.uniforms.uTintK.value = k; m.material.uniforms.uTint.value.set(color); }
  },
  jaw(open = 0, ahh = 0) { openJaw(open, ahh); },
  render,
  // the whole head as one flat shape, for the faded silhouette
  // section: only what the cut plane passes through (a back face seen through the cut is inside a solid)
  mask(pattern, section = false) {
    const re = pattern ? new RegExp(pattern, "i") : null, was = meshes.map((m) => m.visible), mat = section ? sectionMat : maskMat;
    mat.clippingPlanes = planes();
    meshes.forEach((m) => { m.visible = !re || re.test(m.userData.name) || re.test(m.userData.cls); m.userData.saved2 = m.material; m.material = mat; });
    renderer.setRenderTarget(null); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera);
    const url = renderer.domElement.toDataURL("image/png");
    meshes.forEach((m, i) => { m.visible = was[i]; m.material = m.userData.saved2; });
    return url;
  },
  // which structure is in front at every pixel: an id-coloured image and its legend
  ids() {
    for (const m of meshes) { m.userData.saved = m.material; m.material = m.userData.idMat; m.material.clippingPlanes = planes(); }
    renderer.setRenderTarget(null); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera);
    for (const m of meshes) m.material = m.userData.saved;
    const legend = {}; for (const m of meshes) if (m.visible) legend[m.userData.name] = "#" + m.userData.idMat.uniforms.uId.value.getHexString(THREE.LinearSRGBColorSpace);
    return { url: renderer.domElement.toDataURL("image/png"), legend };
  },
  // a lesion painted on a surface: a flattened, irregular disc laid on the point along its normal
  decal(p, n, size, color, seed = 1) {
    const g = new THREE.CircleGeometry(size, 24), pos = g.attributes.position;
    let r = seed; const rnd = () => ((r = (r * 16807) % 2147483647) / 2147483647);
    for (let i = 1; i < pos.count; i++) { const f = 0.8 + 0.4 * rnd(); pos.setXY(i, pos.getX(i) * f, pos.getY(i) * f * 1.6); }
    const m = new THREE.Mesh(g, material("mucosa")); m.material.uniforms.uColor.value.set(color); m.material.uniforms.uWet.value = 0.2;
    m.material.polygonOffset = true; m.material.polygonOffsetFactor = -4;
    m.position.set(...p).addScaledVector(new THREE.Vector3(...n), 0.0004); m.lookAt(new THREE.Vector3(...p).add(new THREE.Vector3(...n)));
    m.userData = { name: "Lesion", cls: "lesion", group: "lesion", idMat: meshes[0].userData.idMat };
    scene.add(m); meshes.push(m); window._decal = m; return m.uuid;
  },
  decalScale(k) { if (window._decal) { window._decal.scale.setScalar(Math.max(k, 0.001)); window._decal.visible = k > 0.01; } },
  project(x, y, z) { const p = new THREE.Vector3(x, y, z).project(camera); return [(p.x * 0.5 + 0.5), (-p.y * 0.5 + 0.5)]; },
  names: () => [...byName.keys()].sort(),
  groups: () => meshes.reduce((a, m) => (a[m.userData.group] = (a[m.userData.group] || 0) + 1, a), {}),
  box(pattern) { const re = new RegExp(pattern, "i"), b = new THREE.Box3(); meshes.filter((m) => re.test(m.userData.name)).forEach((m) => b.expandByObject(m)); return [b.min.toArray(), b.max.toArray()]; },
  // nearest surface point of a structure along a screen ray (for pinning lesions and labels)
  hit(px, py, pattern) {
    camera.updateMatrixWorld(); const ray = new THREE.Raycaster(); ray.setFromCamera(new THREE.Vector2(px * 2 - 1, -(py * 2 - 1)), camera);
    const re = pattern ? new RegExp(pattern, "i") : null;
    const hits = ray.intersectObjects(meshes.filter((m) => m.visible && (!re || re.test(m.userData.name))), false)
      .filter((h) => planes().every((pl) => pl.distanceToPoint(h.point) >= 0));
    return hits.length ? { name: hits[0].object.userData.name, p: hits[0].point.toArray(), n: hits[0].face.normal.clone().transformDirection(hits[0].object.matrixWorld).toArray() } : null;
  },
};
const maskMat = new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide });
const sectionMat = new THREE.ShaderMaterial({ vertexShader: ID_VERT, side: THREE.DoubleSide, clipping: true,
  fragmentShader: "#include <clipping_planes_pars_fragment>\nvoid main(){\n#include <clipping_planes_fragment>\ngl_FragColor = gl_FrontFacing ? vec4(0.0) : vec4(1.0); }" });

new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).load(window.MODEL_URL || "head.glb", (gltf) => {
  const root = gltf.scene; root.updateMatrixWorld(true);
  const all = [];
  root.traverse((o) => { if (o.isMesh) all.push(o); });
  let n = 0;
  for (const o of all) {
    const node = o.userData.cls ? o : o.parent;
    const cls = node.userData.cls || "sense";
    const name = (node.userData.label || node.name || o.name).replace(/\.0\d\d$/, "");
    const group = groupOf(name.replace(/\.(l|r)$/, ""), cls);
    o.userData.cls = cls; o.userData.name = name; o.userData.group = group;
    // everything stays in the scene so the silhouette mask can use the whole head; only plate groups get materials
    o.material = group ? material(group) : material("brain");
    n++; const idc = new THREE.Color().setHex(((n * 2654435761) >>> 8) & 0xffffff);
    o.userData.idMat = new THREE.ShaderMaterial({ uniforms: { uId: { value: idc } }, vertexShader: ID_VERT, fragmentShader: ID_FRAG, side: THREE.DoubleSide, clipping: true });
    meshes.push(o); if (!byName.has(name)) byName.set(name, []); byName.get(name).push(o);
  }
  scene.add(root); root.updateMatrixWorld(true);
  rigJaw();
  window.pl.size(W0, H0, 1);
  document.body.dataset.ready = "1";
}, undefined, (e) => { document.body.dataset.error = String(e && e.message || e); });
